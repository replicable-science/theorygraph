# Human-coded benchmark: protocol (not yet run)

Status: **planned for Stage 2. No human coding exists yet.** This protocol fixes the design now, so the result cannot be shaped after the fact.

## Question

How closely does each model's theory graph match the graph that trained human coders produce from the same transcript, relative to how closely two human coders match each other?

## Sample

* About 40 pitches drawn at random from the 375, seeded (seed to be fixed and published before sampling). Stratification variables are fixed in advance and use no outcome: event era (three bands) and premise-count tercile of the GPT-4o-mini consensus list. Sampling probabilities are recorded, so that design-based supervised learning can use the sample to correct regressions that use model-coded variables (Egami et al., 2023).
* The three hold-out pitches used as worked examples in the 2026 codebooks are excluded from the sample and used for training.
* A separate development set of 10 pitches, disjoint from the benchmark, is used to calibrate prompts for status, links and challenge. The benchmark is not used for tuning.

## Coders

Two trained coders, independent, blind to model output and to venture outcomes. Training on the hold-out pitches with the codebook (`codebook.md` and the prompt files) until they agree on premise lists at the level set before coding. Coding sheets: `coding_sheet_template.csv`. Adjudication happens only after agreement statistics are computed and stored.

## Units and measures

| Unit | Human codes | Agreement measure |
|---|---|---|
| Premises | list of premises, each with a quoted passage | matched by passage overlap (at least 50% of the shorter passage's words in common); report precision and recall of each coder against the other, and α on counts |
| Counts | premises per pitch | Krippendorff's α, ratio level |
| Domains | partition of the matched premises | adjusted Rand index per pitch, bootstrap intervals over pitches |
| Status | one of four per matched premise | Cohen's κ (and κ for asserted vs other) |
| Links | endpoints with passage | edge-level F1 on matched premises |
| Challenge | exchange target and response | κ on response for matched exchanges; share of exchanges matched |

## Comparisons

Human against human sets the ceiling. Each model (GPT-4o-mini, GPT-4.1, at least one stronger or open-weight model that runs on accessible infrastructure) against each coder. The cross-model audit of `theorygraph/audit.py` is repeated on the same pitches. All statistics are reported whatever they are, including low agreement between the humans.

## What would change our conclusions

* If human coders agree with each other far more than models agree with them, models are not yet a substitute and the instrument is the human-coded benchmark with models as a scaling aid under correction.
* If one model sits near the human ceiling and the others do not, that model is the instrument and the disagreement among models is a finding about model choice.
* If human coders also disagree, the construct is the problem. We would revise the codebook and report that.

## Costs

Coder hours and budget: withheld for blind review.
