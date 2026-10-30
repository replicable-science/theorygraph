# Limitations, and what is measured or planned

| Claim | Status | Where |
|---|---|---|
| A model's premise count and grouping are stable on rerun | **Measured**, 375 pitches | `results/audit.json` |
| Different models disagree on premise count and grouping | **Measured**, 375 pitches | `results/audit.json` |
| Quoted passages are in the transcript | **Measured**, all 18,348 premises | `data/derived/premises_long.csv` |
| Evidential status, stated links and Q&A challenge can be extracted | **Shown on three fictional pitches only**; real pitches are Stage 2 | `results/graphs/` |
| These new measures are reliable across coders | **Not shown** | |
| Models agree with human coders | **Planned.** No human coding exists yet | `benchmark/PROTOCOL.md` |
| An open-weight model can do the extraction | **To be tested** with stronger models; Qwen3-32B passed the schema check for 20% of files | `data/derived/schema_validity.json` |
| Stated dependencies fall within domains more than chance | **Planned** (Stage 2): needs the dependency pass on all pitches | |
| Clearer domain separation goes with survival | **Exploratory**: one association, 72 closures on TechCrunch's listing, which can miss closures; weaker with an embedding-based measure (p = 0.14). Not causal | `results/decomposability.json` |
| Survival is an inverted U in theory breadth | **Exploratory**: same 72 closures; peak at about 10 premises, but only 5 pitches have 13 or more; premise counts depend on the model | `results/decomposability.json` |
| Any relation with funding | **Not tested.** Funding is Crunchbase data and not shared | |

## Things that can be wrong

1. **Prompt development.** Codebook 3.0.0 (status, links, challenge) was written and revised on the three fictional pitches only; it was revised after a first look at one fictional pitch, three sentences in total, and the first replies were discarded. Calibration against a separate development set of real pitches is planned.
2. **Public prompts are not the as-run prompts** for passes A and C (three third-party transcripts removed). See `prompts/README.md`.
3. **Source check scope.** It tests words, not meaning. A real sentence used for a wrong claim passes.
4. **Q&A.** No speaker labels. Exchanges coded as "not in the premise list" are partly an effect of the premise rules, which exclude financing, traction and credentials.
5. **Grouping comparisons mix label systems.** Comparisons across free-form domains and fixed labels (ten labels, three tags) are comparisons of partitions only. The cleanest like-for-like comparison is Grok versus Gemini with the same ten labels.
6. **Models change.** Hosted models are updated or retired. Stored replies keep every result reproducible, but a new run may differ.
7. **GPT-4o-mini consensus list.** The premise list shown to groupers is the run whose count is closest to the median of three. Files that failed the study's validator (13%) are not excluded from it; the lists here were built from all files.
8. **Statistics.** Agreement metrics are descriptive. Intervals resample pitches and ignore dependence between runs of one model. The Spearman–Brown value assumes parallel runs.
9. **Selection.** The 375 pitches are those with transcripts of sufficient length; Startup Battlefield is not a random sample of startups, and its pitches are rehearsed and short.
10. **Fictional examples are easy.** They were written to show every feature; real pitches are messier.
11. **Cost and time.** Per-call token counts and latency of live calls are in `logs/`. They are not a forecast for other models.
12. **Not yet done:** human benchmark; longer, deeper sources; open-weight comparison; calibration of the new codebook; tests of whether framework-primed prompts bend the extraction.
