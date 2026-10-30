# Use of AI in this repository

**AI as the object of study.** Language models do the extraction that this project audits:

| Task | Model | Where |
|---|---|---|
| Premises, groupings of 375 pitches (2026) | GPT-4o-mini (OpenAI), Grok 4.7 (xAI), Gemini (Google), Claude (Anthropic), Qwen3-32B (open weights) | `data/derived/provenance_of_codings.json` |
| Status, links, challenge, premises and domains: three fictional pitches | GPT-4o-mini and GPT-4.1 (OpenAI), temperature 0 | `examples/cache/`, `logs/runs.jsonl` |

The three fictional pitches were written by an AI coding assistant at the authors' request so that full examples can be shown without third-party text.

**AI as assistant.** A language-model coding assistant helped write and test the code in this repository, and helped draft the prompts for passes D and E, the page `docs/index.html`, and the documentation, working from the authors' design, instructions, data and scripts. The authors reviewed the results and remain responsible for every statement. The assistant's name is withheld for blind review.

**Guards that do not depend on trusting the assistant.**

* Numbers on the page are generated from stored result files, not typed. `python -m theorygraph verify` recomputes the audit and compares it with the stored one.
* Metric code is tested against reference implementations (scikit-learn for the adjusted Rand index, a brute-force implementation of the definition for Krippendorff's α).
* Every model reply is stored with its request hash. Replay never calls a model.
* The earlier audit numbers were recomputed from the shipped data and reproduce the values obtained in the private project: GPT-4o-mini premise-count α 0.805 (single run) and 0.925 (median of three), Grok ten-label self-agreement ARI 0.73. The Grok–Gemini ARI was reported earlier as 0.12 (median 0.06); here Grok run 1 against Gemini gives 0.114 (median 0.063) and the mean over the three Grok runs is 0.113 (median 0.074). The small gap to the earlier 0.12 is not explained; it may be a difference in which pitches were included.

**What AI did not do.** It did not recode the 375 pitches for this repository. Venture outcomes (TechCrunch status) enter only the exploratory survival models in `theorygraph/decomposability.py`, whose specifications are all reported; no measure or prompt was chosen by its relation to outcomes.
