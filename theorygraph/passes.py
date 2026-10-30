"""The four passes that turn a transcript into a theory graph, and the merge that joins their outputs.

    A  premises      what the speaker treats as necessary for the venture to create value   (codebook 2.1.1)
    C  domains       which premises would have to be revised together                       (codebook 2.1.0)
    D  links_status  how each premise is supported, and the dependences the speaker states  (codebook 3.0.0)
    E  challenge     which premises the question-and-answer session tested, and the reply  (codebook 3.0.0)

Passes A and C use the message construction of the original study, copied unchanged below, so that a run here
differs from the 2026 coding only in the model, the date, and the public copies of the codebooks.
(Pass B of the original study, composition tagging, is not part of this repository.)
"""
from __future__ import annotations

from pathlib import Path

from . import schema
from .llm import Chat
from .sourcecheck import check_graph
from .util import PROMPTS, natural_key, parse_json_reply, sha256_text

PASS_FILES = {
    "premises": ("v2_1_1_premises.public.md", "2.1.1"),
    "domains": ("v2_1_0_domains.public.md", "2.1.0"),
    "links_status": ("v3_0_0_links_status.md", "3.0.0"),
    "challenge": ("v3_0_0_challenge.md", "3.0.0"),
}
SYSTEM = "You are a trained research coder. Return JSON only, conforming to the codebook schema. No prose outside the JSON object."


def codebook_text(pass_name: str) -> str:
    # line ends are normalised so that a Windows checkout and a Linux checkout build the same request (and hash)
    return (PROMPTS / PASS_FILES[pass_name][0]).read_bytes().decode("utf-8").replace("\r\n", "\n")


def codebook_sha256(pass_name: str) -> str:
    return sha256_text(codebook_text(pass_name))


# --------------------------------------------------------------------------- message construction
def task_header(codebook_version: str, model_id: str) -> str:
    """Copied unchanged from the original study (toolkit/theory_graph/prompts.py)."""
    return f"""# Extraction task — codebook only (v{codebook_version})

Follow the codebook below. Output one JSON object matching the schema.
Do not invent premises not supported by the transcript.
Prefer exact contiguous transcript spans for evidence when possible.
Do not use any outside knowledge about this venture.

MODEL LOCK: You MUST set meta.model_id to "{model_id}" exactly.
"""


def build_user_message(*, codebook_text: str, codebook_version: str, case_id: str, transcript: str, model_id: str,
                       extraction_run: int, frozen_premises: str | None = None) -> str:
    """Copied from the original study; the session-id lines it can add are omitted because they were never used."""
    frozen_block = ""
    if frozen_premises is not None:
        frozen_block = f"""
## Frozen premises (fixed; from Pass A — do not add, remove, merge, split, or rename)

{frozen_premises}
"""
    return f"""{task_header(codebook_version, model_id)}

## Codebook

{codebook_text}

## Case

- case_id: {case_id}
- extraction_run: {extraction_run}
{frozen_block}
## Transcript

{transcript}

## Output meta (required)

meta.codebook_version = "{codebook_version}"
meta.pass = "structure"
meta.case_id = "{case_id}"
meta.extraction_run = {extraction_run}
meta.model_id = "{model_id}"
meta.model_provider = "litellm"
meta.temperature = null
meta.temperature_controlled = false
meta.extracted_at = <ISO-8601>
"""


def build_user_message_v3(*, pass_name: str, codebook_text: str, codebook_version: str, case_id: str, transcript: str,
                          transcript_label: str, model_id: str, extraction_run: int, frozen_premises: str,
                          value_line: str | None) -> str:
    value_block = f"\n## Value (fixed)\n\n- {value_line}\n" if value_line else ""
    return f"""# Coding task: codebook v{codebook_version}, pass {pass_name}

Follow the codebook below and return one JSON object that matches its output schema.
Use only the text below. Do not use any outside knowledge about this venture.
Every quoted passage must be copied exactly from the {transcript_label}.

MODEL LOCK: set meta.model_id to "{model_id}" exactly.

## Codebook

{codebook_text}

## Case

- case_id: {case_id}
- extraction_run: {extraction_run}

## Frozen premises (fixed; do not add, remove, merge, split, or rename)

{frozen_premises}
{value_block}
## {transcript_label}

{transcript}
"""


def frozen_block(premises: list[dict]) -> str:
    """Same format as the original study's frozen-premise block."""
    return "\n".join(f"- {p['id']}: {p.get('text', '')}" for p in premises)


def messages_for(pass_name: str, *, case_id: str, transcript: str, model_id: str, premises: list[dict] | None = None,
                 value: list[dict] | None = None, extraction_run: int = 1) -> list[dict]:
    fname, version = PASS_FILES[pass_name]
    cb = codebook_text(pass_name)
    if pass_name == "premises":
        user = build_user_message(codebook_text=cb, codebook_version=version, case_id=case_id, transcript=transcript,
                                  model_id=model_id, extraction_run=extraction_run)
    elif pass_name == "domains":
        user = build_user_message(codebook_text=cb, codebook_version=version, case_id=case_id, transcript=transcript,
                                  model_id=model_id, extraction_run=extraction_run, frozen_premises=frozen_block(premises or []))
    else:
        label = "Q&A transcript" if pass_name == "challenge" else "Transcript"
        vline = f"{value[0]['id']}: {value[0]['text']}" if value else None
        user = build_user_message_v3(pass_name=pass_name, codebook_text=cb, codebook_version=version, case_id=case_id,
                                     transcript=transcript, transcript_label=label, model_id=model_id,
                                     extraction_run=extraction_run, frozen_premises=frozen_block(premises or []), value_line=vline)
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


# --------------------------------------------------------------------------- running a case
def run_case(chat: Chat, case_id: str, pitch: str, qa: str | None = None, *, passes=("premises", "domains", "links_status", "challenge"),
             extraction_run: int = 1, frozen: dict | None = None) -> dict:
    """Run the passes in order, merge, validate, source-check. Returns the theory graph with its provenance.

    `frozen` ({"premises": [...], "value": [...]}) skips Pass A and codes the later passes on a premise list that
    already exists, which is how the original study compared coders (everyone codes the same premises).
    """
    graph: dict = {"meta": {"case_id": case_id, "model": chat.model, "mode": chat.mode, "extraction_run": extraction_run,
                            "passes": {}, "validation_problems": []}}
    problems: list[str] = graph["meta"]["validation_problems"]

    def go(pass_name: str, transcript: str, **kw) -> dict:
        msgs = messages_for(pass_name, case_id=case_id, transcript=transcript, model_id=chat.model, extraction_run=extraction_run, **kw)
        rep = chat.complete(msgs, pass_name=pass_name, case_id=case_id, prompt_sha256=codebook_sha256(pass_name))
        graph["meta"]["passes"][pass_name] = {"codebook_file": PASS_FILES[pass_name][0], "codebook_version": PASS_FILES[pass_name][1],
                                              "codebook_sha256": codebook_sha256(pass_name), "request_sha256": rep["key"],
                                              "reply_created_at": rep["created_at"]}
        try:
            return parse_json_reply(rep["text"])
        except Exception as e:  # invalid JSON is recorded, not hidden
            problems.append(f"{pass_name}: reply is not valid JSON ({e.__class__.__name__})")
            return {}

    if frozen is not None:
        prem = [dict(p) for p in frozen["premises"]]
        graph["value"] = [dict(v) for v in frozen.get("value") or []][:1]
        graph["meta"]["passes"]["premises"] = {"source": "frozen premise list supplied by the caller"}
    else:
        a = go("premises", pitch)
        problems += [f"premises: {p}" for p in schema.validate_premises(a)]
        prem = [{"id": p.get("id"), "text": p.get("text", ""), "explicitness": p.get("status"), "evidence_span": p.get("evidence_span", "")}
                for p in a.get("premises") or []]
        graph["value"] = [{k: v.get(k) for k in ("id", "text", "evidence_span")} for v in a.get("value") or []][:1]
    graph["premises"] = prem
    pids = [p["id"] for p in prem]

    if "domains" in passes and prem:
        c = go("domains", pitch, premises=prem)
        problems += [f"domains: {p}" for p in schema.validate_domains(c, pids)]
        graph["domains"] = [{"id": d.get("id"), "name": d.get("name"), "premise_ids": d.get("premise_ids") or []} for d in c.get("domains") or []]

    if "links_status" in passes and prem:
        d = go("links_status", pitch, premises=prem, value=graph["value"])
        vids = [v["id"] for v in graph["value"]]
        problems += [f"links_status: {p}" for p in schema.validate_links_status(d, pids, vids)]
        by_id = {s.get("id"): s for s in d.get("premises") or []}
        for p in prem:
            s = by_id.get(p["id"], {})
            p["status"], p["status_span"], p["status_reason"] = s.get("status"), s.get("status_span", ""), s.get("status_reason", "")
        links = [{k: l.get(k) for k in ("id", "from", "to", "cue", "evidence_span")} for l in d.get("links") or []]
        ok_to = set(pids) | set(vids)
        graph["links"] = [l for l in links if l["from"] in pids and l["to"] in ok_to and l["from"] != l["to"]]
        graph["meta"]["dropped_links"] = [l for l in links if l not in graph["links"]]  # kept for audit, not in the graph

    if "challenge" in passes and prem and qa:
        e = go("challenge", qa, premises=prem)
        problems += [f"challenge: {p}" for p in schema.validate_challenge(e, pids)]
        graph["challenge"] = {"exchanges": [{k: x.get(k) for k in ("id", "targets", "new_condition", "question_span", "answer_span", "response")}
                                            for x in e.get("exchanges") or []]}

    graph["premises"].sort(key=lambda p: natural_key(p["id"]))
    graph["meta"]["source_check"] = check_graph(graph, pitch, qa)
    return graph


def load_example(name: str, root: Path) -> tuple[str, str | None]:
    def read(p: Path) -> str:
        return p.read_bytes().decode("utf-8").replace("\r\n", "\n").strip()

    qa_path = root / f"{name}.qa.txt"
    return read(root / f"{name}.txt"), (read(qa_path) if qa_path.exists() else None)
