# Data card

## Source material

**Startup Battlefield** pitches (TechCrunch, 2009–2023, 39 events): public stage presentations by founders, with a question-and-answer session. The study sample is 375 pitches. Transcripts were produced by speech recognition (faster-whisper, `h2oai/faster-whisper-large-v3-turbo`, English, beam 5, voice-activity filter) from the public recordings. Transcripts are third-party speech and **are not in this repository**. `data/video_sources.csv` lists the public recording and the cut time of each pitch and Q&A segment (746 of 750 segments resolved; four from two pitches are missing). `data/rebuild_transcripts.py` repeats the transcription from those links. It has not been run in this form.

## What is shipped (`data/derived/`)

| File | Rows | Content |
|---|---|---|
| `cases.csv` | 375 | case id, company, event, year, industry, pitch length in words |
| `premises_long.csv` | 18,348 | one row per extracted premise: model, run, premise id, **premise statement written by the model** (left empty and flagged `text_withheld` when it repeats 8 or more consecutive transcript words: 5.9% of GPT-4o-mini, 7.0% of Grok 4.7, 0% of Claude statements), quote check outcome and similarity, quote length in words. The quoted passage itself is **not** included |
| `frozen_premises_gpt4omini.csv` | 2,906 | the consensus premise list that the groupers received (run whose premise count is closest to the median of three); same withholding rule |
| `groupings_long.csv` | 32,428 | one row per premise per grouper and run: group label |
| `qwen3_32b_premise_counts.csv` | 375 | premise counts of the open-weight model (the premise texts were not kept) |
| `venture_outcomes.csv` | 375 | pitch month and the company's status on TechCrunch's Startup Battlefield listing, re-scraped August 2026: open, closed, acquired, ipo. No Crunchbase field |
| `structure_measures.csv` | 375 | numbers only: premises and domains (GPT-4o-mini), mean premise similarity within domains, between domains and overall, and separation (within minus between), in TF-IDF space and with Qwen3-Embedding-8B vectors; US headquarters (from the TechCrunch listing). Computed from full premise statements, so shipped as computed |
| `value_statements.csv` | 375 | the value the pitch promises, as stated by GPT-4o-mini in the consensus run; same withholding rule |
| `provenance_of_codings.json` | | codebook version, model id, provider, temperature, first extraction time for each coding |
| `schema_validity.json` | | share of premise files that passed the study's validator, GPT-4o-mini and Qwen3-32B |

Models: GPT-4o-mini (`openai/gpt-4o-mini`, temperature 0, three runs, codebook 2.1.1 and 2.1.0), Grok 4.7 (three runs, ten-label taxonomy), Gemini (ten-label taxonomy, one run), a 71-type premise catalogue applied by Claude (one run, eight-label grouping), Qwen3-32B (premise counts only). Dates are in `provenance_of_codings.json`. The Claude and Gemini codings were imported from spreadsheets; their prompts are not in this repository.

## Deliberately left out

* Transcripts and the quoted evidence passages of real pitches.
* Any characteristic of the presenters. None is used or shipped.
* Crunchbase fields (exact closure and acquisition dates, funding rounds), which are licensed. Only the TechCrunch status is shipped.
* Any identifying detail of private individuals. Company names are those of public competitors.

## Known issues

* Premise statements are model-written paraphrases; those that copy 8 or more consecutive transcript words are withheld (a test checks that no 12-word run of any transcript appears in shipped files). A statement can still contain a company or product name that the speaker used.
* The Claude catalogue gave a quote for 36% of premises only; its source check is not comparable with the other two.
* Speech recognition without speaker labels. In the Q&A, who is asking is inferred by the model.
* GPT-4o-mini premise files passed the study's validator for 87% of files; the consensus lists here were built from all files, valid or not (the checks here are on quotes). See `LIMITATIONS.md`.

## Fictional data (`examples/`)

Three pitches and Q&A written for this repository. Any resemblance to real companies is coincidental. Every model reply for them is stored in `examples/cache/`.
