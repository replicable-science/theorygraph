# Theory Graph

Making entrepreneurs' value theories observable with AI: a language model reads what founders say into a checkable theory graph.

A founder's pitch states, in effect, a theory of value: conditions the venture relies on (*premises*), which of them would be revised together (*strategic domains*), which depends on which (*stated dependencies*), and how firmly each is supported (*evidential status*). The theory graph writes this down, with every element tied to the passage it comes from, so that founders' theories can be studied as data across thousands of ventures.

Prototype for the *Organization Science* special issue "AI-Assisted Frontiers in Organizational Science" (Stage 1). Interactive demonstration: <https://replicable-science.github.io/theorygraph/>, rebuilt from the stored results by `python -m theorygraph site`.

## Findings so far (375 Startup Battlefield pitches, GPT-4o mini)

| | |
|---|---|
| Theory graphs | An average pitch yields 7.75 premises in 3.4 strategic domains (one layer; pitches are short) |
| Anchored | 96.7% of 8,728 quoted passages occur word for word in the transcript; an invented quote is flagged |
| Stable | Across three runs: premise counts α = 0.81 (0.93 for the median of three); domain groupings ARI 0.85 [0.82, 0.87] |
| Modular | 99% of theories span two or more strategic domains; the largest domain holds about half of a pitch's premises |
| Near-decomposability and survival (exploratory) | Ventures whose domains separate more cleanly were more likely to stay open on TechCrunch's listing (odds ratio 1.35 per SD, p = 0.010; weaker with embeddings, p = 0.14). `results/decomposability.json` |
| Breadth and survival (exploratory) | Inverted U in breadth (number of premises), peaking at about 10 premises (Lind–Mehlum p = 0.010); the decline rests on few theories (5 pitches with 13 or more premises) |
| Robustness | Other models read the same pitches differently (premise counts correlate 0.14 to 0.38 across models), so each graph is reported with its model |
| Not done | **No human benchmark yet** (design in [`benchmark/PROTOCOL.md`](benchmark/PROTOCOL.md)); evidential status, stated dependencies and the judges' Q&A are coded only for the three fictional pitches so far (Stage 2) |

Exact figures, intervals and methods: `results/audit.json`, `results/decomposability.json`, and the page in `docs/`.

## Run it (nothing needs a key or a network)

```bash
pip install -r requirements.txt
python -m theorygraph verify                 # shipped data, hashes and counts agree
python -m theorygraph audit                  # recompute stability, source check and robustness from data/derived/
python -m theorygraph run all --model gpt-4o-mini   # replay stored model replies, offline
python -m theorygraph run all --model gpt-4.1       # the robustness model, also offline
python -m theorygraph site                   # rebuild docs/index.html
pytest
```

Replay answers only from a stored reply whose request hash (model, temperature, full messages) matches exactly; otherwise it stops and says why. To run a model of your own on the three fictional pitches, or on your own text, use `--live`; any OpenAI-compatible endpoint works, including a local server:

```bash
export THEORYGRAPH_BASE_URL=http://localhost:11434/v1     # default: https://api.openai.com/v1
export THEORYGRAPH_API_KEY=...                              # or OPENAI_API_KEY; not needed for local servers
python -m theorygraph run brinelog --live --model <your-model> [--no-temperature]
```

## What the pipeline does

```
transcript ─┬─ A premises ──────────────► premises (+ value), each with a quoted passage
            ├─ C domains  (on A)  ──────► which premises would be revised together
            ├─ D status & links (on A) ─► evidential status per premise; dependences the speaker states
Q&A ────────└─ E challenge (on A) ──────► Stage 2: which premises the questions tested; defend / qualify / concede / deflect
                         every quoted passage ──► source check against its transcript
```

* Prompts are Markdown files in [`prompts/`](prompts/), sent as written. Each reply is stored with the SHA-256 of its prompt and of its request.
* [`theorygraph/sourcecheck.py`](theorygraph/sourcecheck.py) checks that each quoted passage occurs in the transcript (exact after lower-casing and removing punctuation, or near with similarity ≥ 0.85). It never judges meaning.
* [`theorygraph/audit.py`](theorygraph/audit.py) measures stability across runs and, for robustness, agreement with other models: Krippendorff's α (ratio), Spearman, adjusted Rand index per pitch with bootstrap intervals over pitches, and a shuffled-label null.
* Invalid model output is dropped, not repaired, and listed in the graph's metadata.

## Contents

| Path | What |
|---|---|
| `theorygraph/` | package: passes, replay/live chat, source check, metrics, audit, near-decomposability, page builder |
| `prompts/` | the four codebooks and the hashes of the as-run versions |
| `schema/theory_graph.schema.json` | the graph format |
| `examples/pitches/` | three **fictional** pitches with Q&A; `examples/cache/` holds every model reply |
| `results/` | `audit.json`, `decomposability.json`, graphs of the fictional pitches |
| `docs/` | the static page (`index.html`) and standalone SVG figures (`figures/`) |
| `data/derived/` | the codings of the 375 pitches (premise statements, groupings, quote checks); no transcripts |
| `data/video_sources.csv` | public recording links and cut times; `data/rebuild_transcripts.py` (untested in this form) |
| `benchmark/` | the protocol for the human-coded benchmark (not yet run) |
| `provenance/` | scripts that made the shipped data from private files; they cannot run without those files |
| `tests/` | metrics against reference implementations, source check, offline replay, leak checks |
| `DATA_CARD.md`, `ETHICS.md`, `LIMITATIONS.md`, `AI_USE.md`, `codebook.md` | the documents a reviewer will want |

## What is and is not here

* **Shared:** codings, prompts and hashes, fictional examples with all replies, code, tests.
* **Not shared:** transcripts of real pitches (third-party speech), quoted passages of real pitches, Crunchbase fields (licensed: exact dates, funding), any characteristic of the presenters. Each venture's status on TechCrunch's listing is in `data/derived/venture_outcomes.csv`.
* The prompts for passes A and C are public copies of the codebooks used in 2026, with three third-party worked-example transcripts removed. They are not byte-identical to the as-run files; both hashes are in `prompts/README.md`.

## Licence and citation

Code: MIT ([`LICENSE`](LICENSE)). Derived data and documentation: CC BY 4.0 ([`DATA_LICENSE.md`](DATA_LICENSE.md)). Please cite using [`CITATION.cff`](CITATION.cff).
