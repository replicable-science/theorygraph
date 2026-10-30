"""Export the venture outcome from the authors' private working project.

PROVENANCE ONLY. Reads files that are not in this repository and writes `data/derived/venture_outcomes.csv`:
one row per pitch with the pitch month and the company's status on TechCrunch's Startup Battlefield listing
(re-scraped August 2026): open, closed, acquired or ipo.

Left out on purpose
  - every Crunchbase field (closure and acquisition dates, funding rounds): licensed
  - the other outcome sources of the private project (web search, Wayback Machine, web verification)
  - any characteristic of the presenters

    TG_PRIVATE_ROOT=<private project> python provenance/export_outcomes.py
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

ART = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ["TG_PRIVATE_ROOT"])
DV = ROOT / "data/corpora/startup_battlefield/survival_dv/survival_dv.csv"
OUT = ART / "data" / "derived" / "venture_outcomes.csv"

cases = pd.read_csv(ART / "data" / "derived" / "cases.csv", dtype=str)[["case_id"]]
dv = pd.read_csv(DV, dtype=str)
dv = dv[dv.case_match_status == "matched"]
dv = dv.assign(pitch_month=dv.origin_date.str[:7],
               techcrunch_status=dv.exit_type.map({"failure": "closed", "acquired": "acquired", "ipo": "ipo", "censored": "open"}))
out = cases.merge(dv[["case_id", "pitch_month", "techcrunch_status"]], on="case_id", how="left").sort_values("case_id")
assert len(out) == 375 and out.techcrunch_status.notna().all()
out.to_csv(OUT, index=False, lineterminator="\n")
print(f"wrote {OUT.relative_to(ART)}: {len(out)} rows")
