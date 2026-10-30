"""Export the shareable derived data from the authors' private working project.

PROVENANCE ONLY. This script reads files that are not in this repository (transcripts, raw model
outputs and licensed outcome data) and writes the files in `data/derived/`. It is
included so that reviewers can see exactly what was exported and, just as important, what was left out.

Left out on purpose
  - transcripts and the verbatim evidence spans (third-party speech; see DATA_CARD.md)
  - any characteristic of the presenters
  - outcome dates and any Crunchbase-derived fields (licence)

Set TG_PRIVATE_ROOT to the private project and run it with that project's Python environment:
    TG_PRIVATE_ROOT=<private project> python provenance/export_from_private_project.py
"""
from __future__ import annotations

import glob
import importlib.util
import json
import os
import sys
from pathlib import Path

import pandas as pd

ART = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ART))
from theorygraph.sourcecheck import check_span, normalize  # noqa: E402

ROOT = Path(os.environ["TG_PRIVATE_ROOT"])  # the authors' private project (not in this repository)
RUN = ROOT / "reference/full_n375_k3_v211_gpt4o_mini"
ENC = RUN / "encodings"
QWEN = ROOT / "reference/full_n375_k3_v211_qwen3_32b"
TRANSCRIPTS = ROOT / "data/corpora/startup_battlefield/transcripts"
OUT = ART / "data" / "derived"
OUT.mkdir(parents=True, exist_ok=True)


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


sample = pd.read_csv(ROOT / "data/corpora/startup_battlefield/samples/full_n375.csv", dtype=str)
case_ids = sorted(sample.case_id)
assert len(case_ids) == 375

# ---------------------------------------------------------------- cases (no demographic fields)
cases = pd.read_csv(ROOT / "data/corpora/startup_battlefield/cases.csv", dtype={"case_id": str})
cases = cases[cases.case_id.isin(case_ids)]
cases = cases[["case_id", "name", "event", "year", "industry", "word_count"]].rename(columns={"name": "company", "word_count": "pitch_words"})
cases.sort_values("case_id").to_csv(OUT / "cases.csv", index=False)

# ---------------------------------------------------------------- public video sources (YouTube ids + cut times)
spec = importlib.util.spec_from_file_location("retr", ROOT / "scripts/retranscribe_all.py")
sys.path.insert(0, str(ROOT / "toolkit"))
retr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(retr)
pp = pd.read_csv(retr.PP_CSV)
pp_by_id = pp.set_index("id")
rows = []
for _, c in cases.iterrows():
    for segment in ("PITCH", "Q&A"):
        csv_id = retr.resolve_csv_id(c.case_id, c.company, c.event, segment, pp)
        if csv_id and csv_id in pp_by_id.index:
            r = pp_by_id.loc[csv_id]
            rows.append({"case_id": c.case_id, "segment": segment, "source_id": csv_id, "video_url": r.raw_video_remotepath,
                         "start": r.subsegment_start, "end": r.subsegment_end})
        else:
            rows.append({"case_id": c.case_id, "segment": segment, "source_id": "", "video_url": "", "start": "", "end": ""})
vs = pd.DataFrame(rows).sort_values(["case_id", "segment"])
vs.to_csv(ART / "data" / "video_sources.csv", index=False)
print("video sources resolved:", int((vs.video_url != "").sum()), "of", len(vs))

# ---------------------------------------------------------------- premises, with source check on each model's quoted span
norm_cache: dict[str, str] = {}


def transcript_norm(cid: str) -> str:
    if cid not in norm_cache:
        norm_cache[cid] = normalize((TRANSCRIPTS / f"{cid}.txt").read_text(encoding="utf-8", errors="ignore"))
    return norm_cache[cid]


SHINGLE = 8  # a model-written statement that repeats this many consecutive transcript words is withheld
shingle_cache: dict = {}


def overlaps_transcript(text: str, cid: str) -> bool:
    if cid not in shingle_cache:
        w = transcript_norm(cid).split()
        shingle_cache[cid] = {" ".join(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1)}
    t = normalize(text).split()
    return any(" ".join(t[i:i + SHINGLE]) in shingle_cache[cid] for i in range(len(t) - SHINGLE + 1))


MODELS = [("gpt4omini", "premises__v211__gpt4omini", (1, 2, 3)),
          ("grok47", "premises__v211__grok47", (1, 2, 3)),
          ("claude_catalogue", "premises__claude_v1__claude", (1,))]
prem_rows = []
for model, folder, runs in MODELS:
    for r in runs:
        for cid in case_ids:
            doc = load(ENC / folder / f"run{r}" / f"{cid}.json")
            for p in doc.get("premises") or []:
                outcome, ratio = check_span(p.get("evidence_span"), transcript_norm(cid))
                txt, det = p.get("text", ""), (p.get("condition", "") if model == "claude_catalogue" else "")
                withheld = overlaps_transcript(txt, cid) or overlaps_transcript(det, cid)
                prem_rows.append({"model": model, "run": r, "case_id": cid, "premise_id": p.get("id"),
                                  "text": "" if withheld else txt, "detail": "" if withheld else det, "text_withheld": withheld,
                                  "span_check": outcome, "span_similarity": ratio,
                                  "span_words": len(str(p.get("evidence_span") or "").split())})
prem = pd.DataFrame(prem_rows)
prem.to_csv(OUT / "premises_long.csv", index=False)
print("premises rows", len(prem), prem.groupby("model").size().to_dict())
print("statements withheld (repeat 8+ transcript words):", prem.groupby("model").text_withheld.mean().round(3).to_dict())

# ---------------------------------------------------------------- frozen premise list used by the four groupers on the GPT premises
frozen_rows = []
consensus_run: dict[str, int] = {}
for cid in case_ids:
    cands = {r: load(ENC / "premises__v211__gpt4omini" / f"run{r}" / f"{cid}.json") for r in (1, 2, 3)}
    counts = sorted(len(c.get("premises") or []) for c in cands.values())
    med = counts[1]
    r_pick = min(cands, key=lambda r: abs(len(cands[r].get("premises") or []) - med))
    consensus_run[cid] = r_pick
    for p in cands[r_pick].get("premises") or []:
        frozen_rows.append({"case_id": cid, "consensus_run": r_pick, "premise_id": p["id"],
                            "text": "" if overlaps_transcript(p.get("text", ""), cid) else p.get("text", ""),
                            "text_withheld": overlaps_transcript(p.get("text", ""), cid)})
pd.DataFrame(frozen_rows).to_csv(OUT / "frozen_premises_gpt4omini.csv", index=False)

# ---------------------------------------------------------------- groupings (assignments of premises to groups)
GROUPERS = [("within_gpt4omini", "domains__v210__gpt4omini[premises__v211__gpt4omini]", (1, 2, 3), "domains"),
            ("fu_grok47", "domains__fu__grok47[premises__v211__gpt4omini]", (1, 2, 3), "domains"),
            ("fu_gemini", "domains__fu__gemini[premises__v211__gpt4omini]", (1,), "domains"),
            ("dfv_gpt4omini", "domains__dfv__gpt4omini[premises__v211__gpt4omini]", (1, 2, 3), "assignments"),
            ("sb_claude", "domains__sb__claude[premises__claude_v1__claude]", (1,), "domains")]
grp_rows = []
for grouper, folder, runs, kind in GROUPERS:
    for r in runs:
        for cid in case_ids:
            doc = load(ENC / folder / f"run{r}" / f"{cid}.json")
            if kind == "domains":
                for d in doc.get("domains") or []:
                    for pid in d.get("premise_ids") or []:
                        grp_rows.append({"grouper": grouper, "run": r, "case_id": cid, "premise_id": pid, "group": d.get("name")})
            else:
                for a in doc.get("assignments") or []:
                    grp_rows.append({"grouper": grouper, "run": r, "case_id": cid, "premise_id": a.get("premise_id"), "group": a.get("tag")})
grp = pd.DataFrame(grp_rows)
grp.to_csv(OUT / "groupings_long.csv", index=False)
print("grouping rows", len(grp), grp.groupby("grouper").size().to_dict())

# ---------------------------------------------------------------- Qwen3-32B: only per-pitch counts survive in the private project
q = pd.read_csv(QWEN / "aggregated/dataset.csv")
q = q[q.case_id.isin(case_ids)][["case_id", "breadth", "breadth_run_sd"]].rename(columns={"breadth": "premises_median_of_3"})
q.sort_values("case_id").to_csv(OUT / "qwen3_32b_premise_counts.csv", index=False)

# sanity: the GPT median-of-3 count equals the private dataset's `breadth`
g = pd.read_csv(RUN / "aggregated/dataset.csv")[["case_id", "breadth"]]
med = prem[prem.model == "gpt4omini"].groupby(["case_id", "run"]).size().groupby("case_id").median()
chk = g.set_index("case_id").breadth.reindex(med.index)
print("GPT median-of-3 equals private dataset breadth for", int((chk == med).sum()), "of", len(med), "pitches")

# ---------------------------------------------------------------- provenance of each model/coding
meta = {}
for name, folder in [("premises_gpt4omini", "premises__v211__gpt4omini"), ("premises_grok47", "premises__v211__grok47"),
                     ("premises_claude_catalogue", "premises__claude_v1__claude"),
                     ("grouping_within_gpt4omini", "domains__v210__gpt4omini[premises__v211__gpt4omini]"),
                     ("grouping_fu_grok47", "domains__fu__grok47[premises__v211__gpt4omini]"),
                     ("grouping_fu_gemini", "domains__fu__gemini[premises__v211__gpt4omini]"),
                     ("grouping_dfv_gpt4omini", "domains__dfv__gpt4omini[premises__v211__gpt4omini]"),
                     ("grouping_sb_claude", "domains__sb__claude[premises__claude_v1__claude]")]:
    files = sorted(glob.glob(glob.escape(str(ENC / folder)) + "/run*/*.json"))
    m0 = load(Path(files[0]))["meta"]
    stamps = sorted({load(Path(f))["meta"].get("extracted_at", "") for f in files[:: max(len(files) // 12, 1)]})
    meta[name] = {k: m0.get(k) for k in ("codebook_version", "model_id", "model_provider", "temperature", "source_file")}
    meta[name]["runs"] = len(glob.glob(glob.escape(str(ENC / folder)) + "/run*"))
    meta[name]["first_extracted_at"] = next((s for s in stamps if s), None)
(OUT / "provenance_of_codings.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

# share of premise files that passed the study's schema and verbatim-span validator (from each run's reliability report)
import re  # noqa: E402

validity = {}
for tag, folder in [("gpt4omini", RUN), ("qwen3_32b", QWEN)]:
    txt = (folder / "validation/reliability_report.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*premises\*\*: (\d+)% valid \((\d+) files", txt)
    validity[tag] = {"premise_files": int(m.group(2)), "share_valid": int(m.group(1)) / 100}
(OUT / "schema_validity.json").write_text(json.dumps(validity, indent=2), encoding="utf-8")
print("done")
