"""Venture outcome (data/derived/venture_outcomes.csv): the company's status on TechCrunch's Startup Battlefield
listing, re-scraped August 2026 (open, closed, acquired, ipo). A venture counts as closed only if TechCrunch lists it
as closed; acquisitions and IPOs are not closures. No regression on this outcome is used to choose a measure.
"""
from __future__ import annotations

import pandas as pd

from .util import DERIVED


def load() -> pd.DataFrame:
    return pd.read_csv(DERIVED / "venture_outcomes.csv", dtype=str, keep_default_na=False)


def outcome_summary() -> dict:
    d = load()
    return {"pitches": int(len(d)), "source": "TechCrunch Startup Battlefield listing, re-scraped August 2026",
            "techcrunch": {k: int(v) for k, v in d.techcrunch_status.value_counts().items()}}
