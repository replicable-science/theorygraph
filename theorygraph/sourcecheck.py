"""Source check: does the passage a model quotes for a claim actually occur in the transcript?

This is the project's main guard against invented claims. It never judges meaning, only
whether the quoted words are in the text. Three outcomes:

  verbatim  the quote occurs in the transcript after lower-casing and removing punctuation
  near      a window of the transcript matches the quote with similarity >= NEAR_THRESHOLD
  none      a quote was given but no such window exists (the quote is not in the text)
  no_quote  the model gave no quote at all (reported separately, not counted as unsupported)
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher

NEAR_THRESHOLD = 0.85

_NON_WORD = re.compile(r"[^a-z0-9 ]+")
_SPACE = re.compile(r"\s+")


def normalize(text: str | None) -> str:
    return _NON_WORD.sub("", _SPACE.sub(" ", (text or "").lower())).strip()


def check_span(span: str | None, transcript_norm: str) -> tuple[str, float]:
    """Return (outcome, similarity). `transcript_norm` must already be normalised."""
    s = normalize(span)
    if not s:
        return "no_quote", 0.0
    if s in transcript_norm:
        return "verbatim", 1.0
    words = s.split()
    t_words = transcript_norm.split()
    n = len(words)
    if n == 0 or len(t_words) == 0:
        return "none", 0.0
    best = 0.0
    last = max(len(t_words) - n, 0)
    for i in range(0, last + 1):
        window = " ".join(t_words[i : i + n])
        r = SequenceMatcher(None, window, s).ratio()
        if r > best:
            best = r
            if best >= 0.97:
                break
    return ("near" if best >= NEAR_THRESHOLD else "none"), round(best, 3)


def check_graph(graph: dict, transcript: str, qa_transcript: str | None = None) -> dict:
    """Annotate every quoted span in a graph with its source-check outcome; return a summary.

    Spans checked: premise evidence, status cues, link passages (against the pitch transcript) and
    question and answer passages (against the Q&A transcript). A blank status cue (status `asserted`)
    and a blank answer for `no_answer` are not quotes and are skipped.
    """
    t = normalize(transcript)
    q = normalize(qa_transcript) if qa_transcript else None
    counts = {"verbatim": 0, "near": 0, "none": 0, "no_quote": 0}
    by_kind: dict[str, dict[str, int]] = {}

    def annotate(item: dict, key: str, kind: str, text: str):
        outcome, ratio = check_span(item.get(key), text)
        item[f"{key}_check"] = {"outcome": outcome, "similarity": ratio}
        counts[outcome] += 1
        by_kind.setdefault(kind, {"verbatim": 0, "near": 0, "none": 0, "no_quote": 0})[outcome] += 1

    for p in graph.get("premises") or []:
        annotate(p, "evidence_span", "premise", t)
        if str(p.get("status_span") or "").strip():
            annotate(p, "status_span", "status_cue", t)
    for link in graph.get("links") or []:
        annotate(link, "evidence_span", "link", t)
    if q is not None:
        for ex in (graph.get("challenge") or {}).get("exchanges") or []:
            annotate(ex, "question_span", "question", q)
            if ex.get("response") != "no_answer":
                annotate(ex, "answer_span", "answer", q)
    quoted = counts["verbatim"] + counts["near"] + counts["none"]
    return {"total": quoted + counts["no_quote"], "quoted": quoted, **counts, "by_kind": by_kind,
            "share_supported": (counts["verbatim"] + counts["near"]) / quoted if quoted else None}
