"""Structure checks for a theory graph. Dependency-free; `schema/theory_graph.schema.json` documents the same shape.

A theory graph has: a value node, premises (each with an evidence span and an evidential status),
domains (groups of premises that would be revised together), links (dependences the speaker states),
and challenges (what the question-and-answer session tested and how the founders responded).
"""
from __future__ import annotations

STATUSES = ("evidence_cited", "speculative", "expected", "asserted")
RESPONSES = ("defends", "qualifies", "concedes", "deflects", "no_answer")


def validate_premises(doc: dict) -> list[str]:
    problems = []
    prem = doc.get("premises")
    if not isinstance(prem, list) or not prem:
        return ["premises missing or empty"]
    ids = [p.get("id") for p in prem]
    if len(set(ids)) != len(ids):
        problems.append("duplicate premise ids")
    for p in prem:
        if not str(p.get("id", "")).startswith("P"):
            problems.append(f"bad premise id {p.get('id')!r}")
        if not str(p.get("text", "")).strip():
            problems.append(f"{p.get('id')}: empty text")
        if not str(p.get("evidence_span", "")).strip():
            problems.append(f"{p.get('id')}: missing evidence_span")
    value = doc.get("value")
    if value is not None and (not isinstance(value, list) or len(value) > 1):
        problems.append("value must have at most one item")
    return problems


def validate_domains(doc: dict, premise_ids: list[str]) -> list[str]:
    problems = []
    seen: dict[str, str] = {}
    for d in doc.get("domains") or []:
        for pid in d.get("premise_ids") or []:
            if pid in seen:
                problems.append(f"{pid} appears in {seen[pid]} and {d.get('id')}")
            seen[pid] = d.get("id")
    missing = [p for p in premise_ids if p not in seen]
    extra = [p for p in seen if p not in premise_ids]
    if missing:
        problems.append(f"premises not assigned: {missing}")
    if extra:
        problems.append(f"unknown premise ids in domains: {extra}")
    return problems


def validate_links_status(doc: dict, premise_ids: list[str], value_ids: list[str]) -> list[str]:
    problems = []
    got = [p.get("id") for p in doc.get("premises") or []]
    if sorted(got) != sorted(premise_ids):
        problems.append(f"status must cover each premise exactly once (got {got})")
    for p in doc.get("premises") or []:
        if p.get("status") not in STATUSES:
            problems.append(f"{p.get('id')}: bad status {p.get('status')!r}")
        if p.get("status") != "asserted" and not str(p.get("status_span", "")).strip():
            problems.append(f"{p.get('id')}: status {p.get('status')} needs a status_span")
    ok_to = set(premise_ids) | set(value_ids)
    for link in doc.get("links") or []:
        if link.get("from") not in premise_ids:
            problems.append(f"{link.get('id')}: from {link.get('from')!r} is not a premise")
        if link.get("to") not in ok_to:
            problems.append(f"{link.get('id')}: to {link.get('to')!r} is unknown")
        if link.get("from") == link.get("to"):
            problems.append(f"{link.get('id')}: self link")
        if not str(link.get("evidence_span", "")).strip():
            problems.append(f"{link.get('id')}: missing evidence_span")
    return problems


def validate_challenge(doc: dict, premise_ids: list[str]) -> list[str]:
    problems = []
    for ex in doc.get("exchanges") or []:
        if ex.get("response") not in RESPONSES:
            problems.append(f"{ex.get('id')}: bad response {ex.get('response')!r}")
        targets = ex.get("targets") or []
        if any(t not in premise_ids for t in targets):
            problems.append(f"{ex.get('id')}: unknown target in {targets}")
        if not targets and not str(ex.get("new_condition", "")).strip():
            problems.append(f"{ex.get('id')}: no target and no new_condition")
        if not str(ex.get("question_span", "")).strip():
            problems.append(f"{ex.get('id')}: missing question_span")
        if ex.get("response") != "no_answer" and not str(ex.get("answer_span", "")).strip():
            problems.append(f"{ex.get('id')}: missing answer_span")
    return problems


def validate_graph(graph: dict) -> list[str]:
    """Check a merged graph end to end. Returns a list of problems (empty means valid)."""
    problems = validate_premises(graph)
    pids = [p["id"] for p in graph.get("premises") or [] if "id" in p]
    vids = [v["id"] for v in graph.get("value") or [] if "id" in v]
    if graph.get("domains") is not None:
        problems += validate_domains(graph, pids)
    for p in graph.get("premises") or []:
        if "status" in p and p["status"] not in STATUSES:
            problems.append(f"{p.get('id')}: bad status {p['status']!r}")
    for link in graph.get("links") or []:
        if link.get("from") not in pids or link.get("to") not in set(pids) | set(vids):
            problems.append(f"{link.get('id')}: link endpoints unknown")
    if graph.get("challenge") is not None:
        problems += validate_challenge(graph["challenge"], pids)
    return problems
