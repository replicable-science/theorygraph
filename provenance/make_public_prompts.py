"""Create the public copies of the two codebooks that were used to code the Startup Battlefield pitches.

The as-run codebooks contain three verbatim hold-out transcripts (third-party speech) as worked examples.
The public copies drop those transcripts and the quoted evidence spans, and keep everything else
(rules, definitions, premise statements, value criteria, notes, output schema). Both SHA-256 hashes are written
to prompts/README.md so that anyone holding the as-run file can confirm it is the file that was used.

PROVENANCE ONLY: needs the private project's prompts/ folder.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

ART = Path(__file__).resolve().parents[1]
PRIVATE = Path(os.environ["TG_PRIVATE_ROOT"]) / "prompts"

NOTICE = ("> **Public copy.** The as-run codebook has three worked examples that quote verbatim hold-out transcripts "
          "(third-party speech). Those transcripts, and the quoted evidence spans, are withheld in this copy. The premise "
          "statements, value criteria and notes are unchanged. See `prompts/README.md` for the hashes of both files.")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def redact(text: str) -> str:
    lines = text.split("\n")
    out, in_s5, in_s6_example = [], False, False
    for ln in lines:
        if ln.startswith("## 5."):
            in_s5 = True
        elif ln.startswith("## ") and in_s5:
            in_s5 = False
        if in_s5:
            if ln.startswith("Three **verbatim hold-out transcripts**"):
                out.append(NOTICE)
                continue
            if ln.startswith("**Transcript"):
                continue
            if ln.startswith("|") and "Evidence span" in ln:
                ln = "| Id | Premise |"
            elif ln.startswith("|---|---|---|"):
                ln = "|---|---|"
            elif re.match(r"^\| P\d+ \|", ln):
                cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
                ln = f"| {cells[0]} | {cells[1]} |"
            ln = re.sub(r" Evidence span: \"[^\"]*\"\.?", "", ln)
        if '"evidence_span": "' in ln and ('{"id": "P' in ln or '{"id": "V' in ln):
            ln = re.sub(r'"evidence_span": "[^"]*"', '"evidence_span": "<verbatim transcript substring>"', ln)
        out.append(ln)
    return "\n".join(out)


rows = []
for src, dst in [("v2_1_1_premises.md", "v2_1_1_premises.public.md"), ("v2_1_0_domains.md", "v2_1_0_domains.public.md")]:
    raw = (PRIVATE / src).read_bytes().decode("utf-8")  # as-run bytes (hash must match the file used)
    pub = redact(raw.replace("\r\n", "\n"))
    (ART / "prompts" / dst).write_bytes(pub.encode("utf-8"))  # bytes: keep LF line ends on Windows
    rows.append((src, sha(raw), dst, sha(pub)))
    print(src, len(raw), "->", dst, len(pub))

readme = ["# Prompts", "",
          "Every prompt is a Markdown file that is sent as written. Nothing is assembled from hidden templates except the "
          "short user-message wrapper in `theorygraph/passes.py`. Change a prompt and its hash changes; every stored reply records the hash.", "",
          "| File | Pass | Used for | SHA-256 |", "|---|---|---|---|",
          "| `v2_1_1_premises.public.md` | A: premises | the Startup Battlefield premise lists (codebook 2.1.1) | see below |",
          "| `v2_1_0_domains.public.md` | C: domains | the within-pitch domain groupings (codebook 2.1.0) | see below |",
          "| `v3_0_0_links_status.md` | D: status and links | new in this proposal, tried on three fictional pitches | `{LS}` |",
          "| `v3_0_0_challenge.md` | E: challenge | new in this proposal, tried on three fictional pitches | `{CH}` |", "",
          "## As-run versus public copies", "",
          "The two codebooks used for the 375 pitches contain three verbatim third-party transcripts as worked examples. "
          "The public copies leave those out (see the note at the top of each). The hashes of the as-run files:", "",
          "| As-run file (private) | SHA-256 as run | Public copy | SHA-256 public |", "|---|---|---|---|"]
for a, ha, b, hb in rows:
    readme.append(f"| `{a}` | `{ha}` | `{b}` | `{hb}` |")
readme += ["", "Consequence: running the public copy of Pass A or C on a new pitch is **not** identical to the 2026 run. It is the same rules "
           "without the three hold-out examples. Treat results from the public copies as a replication attempt, not a re-run.", ""]
ls = sha((ART / "prompts" / "v3_0_0_links_status.md").read_text(encoding="utf-8"))
ch = sha((ART / "prompts" / "v3_0_0_challenge.md").read_text(encoding="utf-8"))
(ART / "prompts" / "README.md").write_bytes("\n".join(readme).replace("{LS}", ls).replace("{CH}", ch).encode("utf-8"))
