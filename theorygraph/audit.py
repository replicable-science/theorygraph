"""The cross-model audit, recomputed from the shipped coded data (data/derived/).

Four questions, each answered from the codings of 375 Startup Battlefield pitches:

 1. Is a coder consistent with itself?       repeated runs of one model on the same pitch
 2. Do different coders agree?                 the same pitches coded by different models
 3. Does the grouping of premises agree?       the same premises grouped by different models, per pitch
 4. Are the quoted passages really there?      each quoted evidence passage checked against its transcript

All statistics are descriptive. Nothing here uses survival, funding or any outcome.
"""
from __future__ import annotations

import itertools
import math
from collections import defaultdict

import numpy as np
import pandas as pd

from .metrics import (adjusted_rand_index, bootstrap_mean_ci, bootstrap_spearman_ci, krippendorff_alpha_ratio, spearman,
                      spearman_brown)
from .util import DERIVED

SEED = 20261030
EXCLUDED_LABELS = {"", "other", "unassigned", "none", "nan"}
MIN_JOINT, MIN_LABELS = 4, 2

MODEL_LABEL = {"gpt4omini": "GPT-4o-mini", "grok47": "Grok 4.7", "claude_catalogue": "Claude (71-type catalogue)", "qwen3_32b": "Qwen3-32B (open weights)"}
GROUPER_LABEL = {
    "within_gpt4omini": "GPT-4o-mini, free-form domains",
    "fu_grok47": "Grok 4.7, ten fixed labels",
    "fu_gemini": "Gemini, ten fixed labels",
    "dfv_gpt4omini": "GPT-4o-mini, three tags",
    "sb_claude": "Claude, eight labels (own premises)",
}


# ------------------------------------------------------------------------------------------------ premise counts
def _counts_by_run(prem: pd.DataFrame, model: str) -> pd.DataFrame:
    d = prem[prem.model == model].groupby(["case_id", "run"]).size().unstack("run")
    return d


def premise_count_audit(prem: pd.DataFrame, qwen: pd.DataFrame, case_ids: list[str]) -> dict:
    out: dict = {"self_consistency": {}, "between_models": {}, "means": {}}
    medians: dict[str, pd.Series] = {}
    for model in ("gpt4omini", "grok47"):
        runs = _counts_by_run(prem, model).reindex(case_ids).fillna(0)
        single = krippendorff_alpha_ratio(runs.to_numpy())
        out["self_consistency"][model] = {"runs": int(runs.shape[1]), "alpha_single_run": single,
                                          "alpha_median_of_3_spearman_brown": spearman_brown(single, 3)}
        medians[model] = runs.median(axis=1)
    cl = _counts_by_run(prem, "claude_catalogue").reindex(case_ids).fillna(0)
    medians["claude_catalogue"] = cl.iloc[:, 0]
    medians["qwen3_32b"] = qwen.set_index("case_id").premises_median_of_3.reindex(case_ids)
    for m, s in medians.items():
        out["means"][m] = {"mean_premises_per_pitch": float(s.mean()), "sd": float(s.std())}
    for a, b in itertools.combinations(medians, 2):
        r, lo, hi = bootstrap_spearman_ci(medians[a].to_numpy(), medians[b].to_numpy(), seed=SEED)
        out["between_models"][f"{a}__{b}"] = {"spearman": r, "ci95": [lo, hi]}

    # like for like: one run against one run, same model versus different model
    single = {m: _counts_by_run(prem, m).reindex(case_ids).fillna(0) for m in ("gpt4omini", "grok47", "claude_catalogue")}
    same, cross = [], {}
    for m in ("gpt4omini", "grok47"):
        cols = single[m].columns
        rs = [spearman(single[m][i].to_numpy(), single[m][j].to_numpy()) for i, j in itertools.combinations(cols, 2)]
        out["self_consistency"][m]["spearman_between_runs_mean"] = float(np.mean(rs))
        same += rs
    for a, b in itertools.combinations(single, 2):
        rs = [spearman(single[a][i].to_numpy(), single[b][j].to_numpy()) for i in single[a].columns for j in single[b].columns]
        cross[f"{a}__{b}"] = float(np.mean(rs))
    out["single_run_like_for_like"] = {"same_model_runs_mean_spearman": float(np.mean(same)), "different_models_mean_spearman": float(np.mean(list(cross.values()))),
                                       "different_models_by_pair": cross}
    return out


# ------------------------------------------------------------------------------------------------ grouping agreement
def _partitions(groupings: pd.DataFrame) -> dict[tuple[str, int], dict[str, dict[str, str]]]:
    parts: dict = defaultdict(lambda: defaultdict(dict))
    for g, r, c, p, lab in groupings[["grouper", "run", "case_id", "premise_id", "group"]].itertuples(index=False):
        parts[(g, int(r))][c][p] = str(lab).strip()
    return parts


def _ari_for_pair(pa: dict, pb: dict, case_ids: list[str]) -> dict[str, float]:
    res = {}
    for c in case_ids:
        a, b = pa.get(c, {}), pb.get(c, {})
        joint = [p for p in a if p in b and a[p].lower() not in EXCLUDED_LABELS and b[p].lower() not in EXCLUDED_LABELS]
        if len(joint) < MIN_JOINT:
            continue
        la, lb = [a[p] for p in joint], [b[p] for p in joint]
        if len(set(la)) < MIN_LABELS or len(set(lb)) < MIN_LABELS:
            continue
        v = adjusted_rand_index(la, lb)
        if not math.isnan(v):
            res[c] = v
    return res


def _mean_over_run_pairs(parts, ga: str, gb: str, case_ids, same_grouper: bool) -> dict[str, float]:
    runs_a = sorted(r for (g, r) in parts if g == ga)
    runs_b = sorted(r for (g, r) in parts if g == gb)
    combos = list(itertools.combinations(runs_a, 2)) if same_grouper else list(itertools.product(runs_a, runs_b))
    per: dict[str, list[float]] = defaultdict(list)
    for ra, rb in combos:
        for c, v in _ari_for_pair(parts[(ga, ra)], parts[(gb, rb)], case_ids).items():
            per[c].append(v)
    return {c: float(np.mean(v)) for c, v in per.items()}


def _null_ari(parts, ga: str, gb: str, case_ids, n_perm: int = 200) -> dict:
    """Same comparison, but with the labels of the second coder shuffled within each pitch."""
    rng = np.random.default_rng(SEED)
    ra, rb = min(r for (g, r) in parts if g == ga), min(r for (g, r) in parts if g == gb)
    pa, pb = parts[(ga, ra)], parts[(gb, rb)]
    items = {}
    for c in case_ids:
        a, b = pa.get(c, {}), pb.get(c, {})
        joint = [p for p in a if p in b and a[p].lower() not in EXCLUDED_LABELS and b[p].lower() not in EXCLUDED_LABELS]
        la, lb = [a[p] for p in joint], [b[p] for p in joint]
        if len(joint) >= MIN_JOINT and len(set(la)) >= MIN_LABELS and len(set(lb)) >= MIN_LABELS:
            items[c] = (la, lb)
    means = []
    for _ in range(n_perm):
        vals = []
        for la, lb in items.values():
            v = adjusted_rand_index(la, rng.permutation(lb).tolist())
            if not math.isnan(v):
                vals.append(v)
        means.append(float(np.mean(vals)))
    return {"null_mean": float(np.mean(means)), "null_p95": float(np.quantile(means, 0.95)), "n_permutations": n_perm}


def grouping_audit(groupings: pd.DataFrame, case_ids: list[str]) -> dict:
    parts = _partitions(groupings)
    out: dict = {"self_consistency": {}, "between_groupers": {}}
    for g in ("within_gpt4omini", "fu_grok47", "dfv_gpt4omini"):
        per = _mean_over_run_pairs(parts, g, g, case_ids, same_grouper=True)
        m, lo, hi = bootstrap_mean_ci(list(per.values()), seed=SEED)
        out["self_consistency"][g] = {"label": GROUPER_LABEL[g], "pitches": len(per), "mean_ari": m, "ci95": [lo, hi],
                                      "median_ari": float(np.median(list(per.values())))}
    for ga, gb in [("fu_grok47", "fu_gemini"), ("within_gpt4omini", "fu_grok47"), ("within_gpt4omini", "fu_gemini"),
                   ("within_gpt4omini", "dfv_gpt4omini"), ("fu_grok47", "dfv_gpt4omini"), ("fu_gemini", "dfv_gpt4omini")]:
        per = _mean_over_run_pairs(parts, ga, gb, case_ids, same_grouper=False)
        m, lo, hi = bootstrap_mean_ci(list(per.values()), seed=SEED)
        null = _null_ari(parts, ga, gb, case_ids)
        out["between_groupers"][f"{ga}__{gb}"] = {
            "a": GROUPER_LABEL[ga], "b": GROUPER_LABEL[gb], "same_task": ga.startswith("fu_") and gb.startswith("fu_"), "pitches": len(per),
            "mean_ari": m, "ci95": [lo, hi], "median_ari": float(np.median(list(per.values()))),
            "share_pitches_ari_below_0.2": float(np.mean(np.asarray(list(per.values())) < 0.2)), **null}
    # distribution of the headline comparison, for the figure
    out["fu_grok_vs_gemini_per_pitch"] = _mean_over_run_pairs(parts, "fu_grok47", "fu_gemini", case_ids, same_grouper=False)
    return out


# ------------------------------------------------------------------------------------------------ source check
def sourcecheck_audit(prem: pd.DataFrame) -> dict:
    out = {}
    for model, d in prem.groupby("model"):
        vc = d.span_check.value_counts().to_dict()
        quoted = sum(vc.get(k, 0) for k in ("verbatim", "near", "none"))
        out[model] = {"premises": int(len(d)), "with_quote": int(quoted), "no_quote": int(vc.get("no_quote", 0)),
                      "verbatim": int(vc.get("verbatim", 0)), "near": int(vc.get("near", 0)), "not_found": int(vc.get("none", 0)),
                      "share_verbatim": vc.get("verbatim", 0) / quoted if quoted else None,
                      "share_verbatim_or_near": (vc.get("verbatim", 0) + vc.get("near", 0)) / quoted if quoted else None}
    return out


# ------------------------------------------------------------------------------------------------ structure
def _describe(s: pd.Series) -> dict:
    return {"mean": float(s.mean()), "sd": float(s.std()), "median": float(s.median()), "min": float(s.min()), "max": float(s.max())}


def structure_audit(prem: pd.DataFrame, groupings: pd.DataFrame, case_ids: list[str]) -> dict:
    """Descriptives of the GPT-4o-mini theory graphs: premises per pitch (median of three runs) and, per pitch and
    grouping run, the number of strategic domains, their size and the share of premises in the largest one."""
    counts = _counts_by_run(prem, "gpt4omini").reindex(case_ids).fillna(0).median(axis=1)
    g = groupings[groupings.grouper == "within_gpt4omini"]
    sizes = g.groupby(["case_id", "run", "group"]).size()
    per = sizes.groupby(["case_id", "run"]).agg(domains="size", premises="sum", largest="max")
    per["largest_share"] = per.largest / per.premises
    dist = per.domains.clip(upper=5).value_counts(normalize=True).sort_index()
    return {"pitches": len(case_ids), "pitch_runs": int(len(per)),
            "premises_per_pitch": _describe(counts),
            "domains_per_pitch": _describe(per.domains),
            "premises_per_domain": _describe(sizes),
            "share_in_largest_domain": _describe(per.largest_share),
            "domains_distribution": {("5+" if k == 5 else str(int(k))): float(v) for k, v in dist.items()}}


# ------------------------------------------------------------------------------------------------ everything
def run_audit() -> dict:
    prem = pd.read_csv(DERIVED / "premises_long.csv", keep_default_na=False)
    groupings = pd.read_csv(DERIVED / "groupings_long.csv", keep_default_na=False)
    qwen = pd.read_csv(DERIVED / "qwen3_32b_premise_counts.csv")
    case_ids = sorted(pd.read_csv(DERIVED / "cases.csv", dtype=str).case_id)
    pc = premise_count_audit(prem, qwen, case_ids)
    gr = grouping_audit(groupings, case_ids)
    sc = sourcecheck_audit(prem)
    bm = pc["between_models"]
    sp = [v["spearman"] for k, v in bm.items() if "qwen" not in k]
    head = {
        "pitches": len(case_ids),
        "premise_count_alpha_gpt_single_run": pc["self_consistency"]["gpt4omini"]["alpha_single_run"],
        "premise_count_alpha_gpt_median_of_3": pc["self_consistency"]["gpt4omini"]["alpha_median_of_3_spearman_brown"],
        "premise_count_spearman_between_models_range": [min(sp), max(sp)],
        "grouping_self_consistency_ari_grok_ten_labels": gr["self_consistency"]["fu_grok47"]["mean_ari"],
        "grouping_ari_grok_vs_gemini_same_ten_labels": gr["between_groupers"]["fu_grok47__fu_gemini"]["mean_ari"],
        "grouping_ari_grok_vs_gemini_median": gr["between_groupers"]["fu_grok47__fu_gemini"]["median_ari"],
        "share_premises_with_quote_found_verbatim_gpt4omini": sc["gpt4omini"]["share_verbatim"],
    }
    from .outcomes import outcome_summary
    return {"headline": head, "structure": structure_audit(prem, groupings, case_ids), "outcomes": outcome_summary(),
            "premise_counts": pc, "grouping": gr, "source_check": sc,
            "labels": {"models": MODEL_LABEL, "groupers": GROUPER_LABEL},
            "method": {"seed": SEED, "min_jointly_labeled_premises": MIN_JOINT, "min_labels_per_partition": MIN_LABELS,
                       "excluded_labels": sorted(EXCLUDED_LABELS - {""}), "bootstrap": "2000 resamples of pitches",
                       "null": "labels of the second coder shuffled within each pitch, 200 permutations"}}
