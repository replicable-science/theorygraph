"""Near-decomposability of founders' value theories (Simon, 1962), from the shipped data only.

 1. Separation. How clearly does a theory separate into its strategic domains? Mean similarity of premises within a
    domain minus between domains, in TF-IDF space and with embeddings (data/derived/structure_measures.csv).
 2. Survival (exploratory). Is clearer separation associated with venture survival? Logit of "not closed" on
    TechCrunch's Startup Battlefield listing, standard errors clustered by event, pitches of at least 300 words.
    Controls are public: pitch length, year, US headquarters, healthcare, mean premise similarity. Every
    specification below is reported whatever its result; none was chosen by its p-value.
 3. Breadth (exploratory). Is survival an inverted U in breadth, the number of premises? Same sample, outcome and controls.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .util import DERIVED

MIN_WORDS = 300


# ------------------------------------------------------------------------------------------------ structure
def similarity_structure() -> dict:
    s = pd.read_csv(DERIVED / "structure_measures.csv")
    out = {}
    for v in ("tfidf", "emb"):
        d = s[[f"within_domain_sim_{v}", f"between_domain_sim_{v}", f"domain_sep_{v}"]].dropna()
        out[v] = {"pitches": int(len(d)), "within_mean": float(d.iloc[:, 0].mean()), "between_mean": float(d.iloc[:, 1].mean()),
                  "sep_mean": float(d.iloc[:, 2].mean()), "sep_sd": float(d.iloc[:, 2].std()), "share_positive": float((d.iloc[:, 2] > 0).mean())}
    return out


# ------------------------------------------------------------------------------------------------ survival
def analysis_frame() -> pd.DataFrame:
    from .outcomes import load as load_outcomes

    cases = pd.read_csv(DERIVED / "cases.csv", dtype={"case_id": str})
    s = pd.read_csv(DERIVED / "structure_measures.csv", dtype={"case_id": str})
    d = cases.merge(s, on="case_id").merge(load_outcomes()[["case_id", "techcrunch_status"]], on="case_id")
    d["survived_tc"] = (d.techcrunch_status != "closed").astype(int)
    d["pitch100"] = d.pitch_words / 100
    d["healthcare"] = (d.industry == "HealthTech, Healthcare").astype(int)
    d = d[d.pitch_words >= MIN_WORDS].dropna(subset=["domain_sep_tfidf", "domain_sep_emb", "premise_sim_emb", "premise_sim_tfidf", "hq_us"]).copy()
    z = lambda x: (x - x.mean()) / x.std(ddof=1)
    d["sep_z"], d["sep_emb_z"], d["sim_z"] = z(d.domain_sep_tfidf), z(d.domain_sep_emb), z(d.premise_sim_emb)
    return d


CONTROLS = "pitch100 + year + hq_us + healthcare + sim_z"
SPECS = [
    ("main", "Separation (TF-IDF), TechCrunch outcome", "survived_tc ~ sep_z + " + CONTROLS, "sep_z"),
    ("with_breadth", "… adding breadth and breadth squared", "survived_tc ~ sep_z + premises + I(premises**2) + " + CONTROLS, "sep_z"),
    ("with_domains", "… adding the number of domains", "survived_tc ~ sep_z + domains + " + CONTROLS, "sep_z"),
    ("embedding", "Separation (embeddings) instead of TF-IDF", "survived_tc ~ sep_emb_z + " + CONTROLS, "sep_emb_z"),
]


def survival_models() -> dict:
    import statsmodels.formula.api as smf

    d = analysis_frame()
    rows = {}
    for key, label, formula, term in SPECS:
        r = smf.logit(formula, data=d).fit(disp=0, cov_type="cluster", cov_kwds={"groups": d.event})
        extra = {k: {"b": float(r.params[k]), "p": float(r.pvalues[k])} for k in r.params.index if k in ("premises", "I(premises ** 2)", "domains")}
        rows[key] = {"label": label, "formula": formula, "term": term, "b": float(r.params[term]), "se": float(r.bse[term]),
                     "p": float(r.pvalues[term]), "odds_ratio_per_sd": float(np.exp(r.params[term])), "n": int(r.nobs), "other": extra}
    outcome = d["survived_tc"]
    return {"sample": {"pitches": int(len(d)), "events": int(d.event.nunique()), "closed_techcrunch": int((1 - outcome).sum()), "min_words": MIN_WORDS},
            "controls": CONTROLS, "clustering": "event", "models": rows}


BREADTH_AT = (4, 7, 10, 14)


def breadth_model() -> dict:
    """Theory breadth (premises) and survival: linear and squared term, with the Lind-Mehlum (2010) test for an
    inverted U over the observed range, the turning point with a delta-method interval, and predicted survival at
    fixed breadths (other variables at their observed values)."""
    import statsmodels.formula.api as smf
    from scipy.stats import norm

    d = analysis_frame()
    r = smf.logit("survived_tc ~ premises + I(premises**2) + " + CONTROLS, data=d).fit(disp=0, cov_type="cluster", cov_kwds={"groups": d.event})
    t1, t2 = "premises", "I(premises ** 2)"
    b1, b2 = float(r.params[t1]), float(r.params[t2])
    V = r.cov_params().loc[[t1, t2], [t1, t2]].to_numpy()
    lo, hi = int(d.premises.min()), int(d.premises.max())

    def slope_z(x):
        g = np.array([1.0, 2.0 * x])
        return (b1 + 2 * b2 * x) / float(np.sqrt(g @ V @ g))

    p_lm = float(max(norm.sf(slope_z(lo)), norm.cdf(slope_z(hi))))
    turn = -b1 / (2 * b2)
    g = np.array([-1 / (2 * b2), b1 / (2 * b2 ** 2)])
    se_turn = float(np.sqrt(g @ V @ g))
    pred = {}
    for k in BREADTH_AT:
        x = d.copy()
        x["premises"] = k
        pred[str(k)] = float(r.predict(x).mean())
    return {"formula": "survived_tc ~ premises + I(premises**2) + " + CONTROLS, "n": int(r.nobs),
            "b_premises": b1, "p_premises": float(r.pvalues[t1]), "b_premises_sq": b2, "p_premises_sq": float(r.pvalues[t2]),
            "turning_point": float(turn), "turning_point_ci95": [float(turn - 1.96 * se_turn), float(turn + 1.96 * se_turn)],
            "lind_mehlum_p": p_lm, "range": [lo, hi], "predicted_survival": pred,
            "pitches_by_premises": {"4-5": int((d.premises <= 5).sum()), "6-9": int(d.premises.between(6, 9).sum()),
                                    "10-12": int(d.premises.between(10, 12).sum()), "13+": int((d.premises >= 13).sum())}}


def run_decomposability() -> dict:
    return {"similarity": similarity_structure(), "survival": survival_models(), "breadth": breadth_model()}
