"""Export the value statement of each pitch (pass A, GPT-4o-mini, the consensus run) from the private project.

PROVENANCE ONLY. Writes `data/derived/value_statements.csv`. A statement that repeats 8 or more consecutive transcript
words is withheld (left empty, `text_withheld` = True), the same rule as for premise statements.

    TG_PRIVATE_ROOT=<private project> python provenance/export_value_statements.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd

ART = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ART))
from theorygraph.sourcecheck import normalize  # noqa: E402

ROOT = Path(os.environ["TG_PRIVATE_ROOT"])
ENC = ROOT / "reference/full_n375_k3_v211_gpt4o_mini/encodings/premises__v211__gpt4omini"
TRANSCRIPTS = ROOT / "data/corpora/startup_battlefield/transcripts"
SHINGLE = 8


def overlaps_transcript(text: str, cid: str) -> bool:
    w = normalize((TRANSCRIPTS / f"{cid}.txt").read_text(encoding="utf-8", errors="ignore")).split()
    sh = {" ".join(w[i:i + SHINGLE]) for i in range(len(w) - SHINGLE + 1)}
    t = normalize(text).split()
    return any(" ".join(t[i:i + SHINGLE]) in sh for i in range(len(t) - SHINGLE + 1))


frozen = pd.read_csv(ART / "data" / "derived" / "frozen_premises_gpt4omini.csv", dtype={"case_id": str})
runs = frozen.groupby("case_id").consensus_run.first()
rows = []
for cid, run in runs.items():
    doc = json.loads((ENC / f"run{int(run)}" / f"{cid}.json").read_text(encoding="utf-8"))
    vals = doc.get("value") or []
    text = " ".join(v.get("text", "") for v in vals).strip()
    withheld = bool(text) and overlaps_transcript(text, cid)
    rows.append({"case_id": cid, "consensus_run": int(run), "text": "" if withheld else text, "text_withheld": withheld})
out = pd.DataFrame(rows).sort_values("case_id")
assert len(out) == 375
out.to_csv(ART / "data" / "derived" / "value_statements.csv", index=False, lineterminator="\n")
print(f"wrote data/derived/value_statements.csv: {len(out)} rows, withheld {out.text_withheld.mean():.1%}, empty {(out.text == '').mean():.1%}")
