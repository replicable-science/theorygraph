"""`python -m theorygraph verify`: do the shipped files agree with each other?

Checks (all offline): required files exist; no column in any shipped table names a personal attribute or an outcome;
every stored model reply matches its request hash; the stored audit equals a fresh recomputation; the prompt
hashes in prompts/README.md match the prompt files.
"""
from __future__ import annotations

import json
import math
import re

import pandas as pd

from .audit import run_audit
from .llm import request_key
from .util import CACHE, DERIVED, PROMPTS, REPO, RESULTS, sha256_text

PERSONAL_COLUMN_TOKENS = {"age", "gender", "race", "bmi", "zbmi"}
OUTCOME_COLUMN_TOKENS = {"survive", "survived", "survival", "fail", "failed", "failure", "funding", "crunchbase", "cb", "raised", "closed", "outcome", "valuation"}
OUTCOMES_FILE = "data/derived/venture_outcomes.csv"  # TechCrunch status only; funding and Crunchbase fields stay out
OUTCOMES_COLUMNS = {"case_id", "pitch_month", "techcrunch_status"}
REQUIRED = ["data/derived/cases.csv", "data/derived/premises_long.csv", "data/derived/groupings_long.csv", "data/derived/frozen_premises_gpt4omini.csv",
            "data/derived/qwen3_32b_premise_counts.csv", "data/derived/venture_outcomes.csv", "data/derived/structure_measures.csv", "results/decomposability.json", "data/derived/provenance_of_codings.json", "data/derived/schema_validity.json",
            "data/video_sources.csv", "results/audit.json", "prompts/README.md", "data/derived/value_statements.csv", "docs/index.html"]


def _close(a, b, tol=1e-9) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_close(a[k], b[k], tol) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_close(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return (a is None and b is None) or (a is not None and b is not None and (math.isclose(a, b, rel_tol=tol, abs_tol=tol)))
    return a == b


def verify_all() -> list[str]:
    problems: list[str] = []
    for rel in REQUIRED:
        if not (REPO / rel).exists():
            problems.append(f"missing file: {rel}")
    for csv in list((REPO / "data").rglob("*.csv")) + list((REPO / "results").glob("**/*.csv")):
        if "restricted" in csv.parts:
            continue
        cols = [c.lower() for c in pd.read_csv(csv, nrows=0).columns]
        rel = csv.relative_to(REPO).as_posix()
        if rel == OUTCOMES_FILE and set(cols) != OUTCOMES_COLUMNS:
            problems.append(f"{rel}: columns differ from the documented public outcome columns")
        for c in cols:
            tokens = set(re.split(r"[^a-z0-9]+", c))
            forbidden = PERSONAL_COLUMN_TOKENS | (set() if rel == OUTCOMES_FILE else OUTCOME_COLUMN_TOKENS)
            if tokens & forbidden or any(t.startswith("attract") for t in tokens):
                problems.append(f"{rel}: column {c!r} names a personal attribute or an outcome")
    n = len(pd.read_csv(DERIVED / "cases.csv"))
    if n != 375:
        problems.append(f"cases.csv has {n} rows, expected 375")
    # stored replies match their requests
    for f in sorted(CACHE.glob("*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        if "messages" in rec and request_key(rec["model"], rec["temperature"], rec["messages"]) != rec["request_sha256"]:
            problems.append(f"{f.name}: stored reply does not match its request hash")
        try:
            json.loads(rec["response_text"])
        except Exception:
            problems.append(f"{f.name}: stored reply is not JSON")
    # stored audit == fresh audit
    fresh, stored = run_audit(), json.loads((RESULTS / "audit.json").read_text(encoding="utf-8"))
    if not _close(fresh, stored):
        problems.append("results/audit.json differs from a fresh recomputation; run `python -m theorygraph audit`")
    from .decomposability import run_decomposability

    if not _close(run_decomposability(), json.loads((RESULTS / "decomposability.json").read_text(encoding="utf-8")), tol=1e-6):
        problems.append("results/decomposability.json differs from a fresh recomputation; run `python -m theorygraph audit`")
    # prompt hashes
    readme = (PROMPTS / "README.md").read_text(encoding="utf-8")
    for name in ("v3_0_0_links_status.md", "v3_0_0_challenge.md", "v2_1_1_premises.public.md", "v2_1_0_domains.public.md"):
        h = sha256_text((PROMPTS / name).read_bytes().decode("utf-8").replace("\r\n", "\n"))
        if h not in readme:
            problems.append(f"prompts/README.md does not list the current hash of {name}")
    return problems
