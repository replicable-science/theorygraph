# Prompts

Every prompt is a Markdown file that is sent as written. Nothing is assembled from hidden templates except the short user-message wrapper in `theorygraph/passes.py`. Change a prompt and its hash changes; every stored reply records the hash.

| File | Pass | Used for | SHA-256 |
|---|---|---|---|
| `v2_1_1_premises.public.md` | A: premises | the Startup Battlefield premise lists (codebook 2.1.1) | see below |
| `v2_1_0_domains.public.md` | C: domains | the within-pitch domain groupings (codebook 2.1.0) | see below |
| `v3_0_0_links_status.md` | D: status and links | new in this proposal, tried on three fictional pitches | `6fa5952efb3b4e409ead074562c63d5e9af86c7203a20d3a80883f02506ce860` |
| `v3_0_0_challenge.md` | E: challenge | new in this proposal, tried on three fictional pitches | `25553e543ca7940e5dc48fe3952b11e8f6b31cd1f94c90beb283a4a0fa9044fe` |

## As-run versus public copies

The two codebooks used for the 375 pitches contain three verbatim third-party transcripts as worked examples. The public copies leave those out (see the note at the top of each). The hashes of the as-run files:

| As-run file (private) | SHA-256 as run | Public copy | SHA-256 public |
|---|---|---|---|
| `v2_1_1_premises.md` | `69713b56e7ee4f1b5b5a928ea44e3e8ea7f019679a729c86b4deedb7c7514e9b` | `v2_1_1_premises.public.md` | `3d9540169855edd480b1fa9008a7d860f4257704e782ea1424ac3aae69d75973` |
| `v2_1_0_domains.md` | `a25eeb32bd3a3adab46027f764aa5c4704b788249373dce85dff1a1ffafc63a8` | `v2_1_0_domains.public.md` | `e8b3d7b51879f042da61195ac75a0e4323b54473073fd63206d3994da3459839` |

Consequence: running the public copy of Pass A or C on a new pitch is **not** identical to the 2026 run. It is the same rules without the three hold-out examples. Treat results from the public copies as a replication attempt, not a re-run.
