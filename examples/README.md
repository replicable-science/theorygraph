# Examples

`pitches/` holds three **fictional** pitches (`brinelog`, `lathework`, `recallpost`), each with a question-and-answer session (`*.qa.txt`). They were written for this repository so that complete theory graphs, with every quoted passage, can be shown and shared. Any resemblance to real companies is coincidental. They are deliberately plain: each contains a mix of claims with evidence, plans, hedged hopes and bare assertions, a few stated dependences, and questions that a panel might ask.

`cache/` holds every model reply that produced `results/graphs/`. Each file is named by the first 20 characters of the request hash, and records the model, temperature, the SHA-256 of the prompt file, token usage, time, and the full request messages. `python -m theorygraph run all --model gpt-4.1` (or `gpt-4o-mini`) rebuilds the graphs from these files without a network.

The same pitches were coded twice, by two models, with identical prompts. Compare `results/graphs/brinelog__gpt-4o-mini.json` and `results/graphs/brinelog__gpt-4.1.json`.
