# Codebook in brief

The prompts in `prompts/` are the instrument. This page restates the constructs in plain language for human coders. If the two ever differ, the prompt files govern.

| Construct | Definition | Decision rule | Prompt |
|---|---|---|---|
| **Premise** | A claim the speaker treats as necessary for the venture to create value, specific enough that it could be shown wrong | List what the venture would have to change if the claim were wrong. Claims that need the same change are one premise; claims that need different changes are separate. When unsure, separate. Exclude the financing ask, greetings, traction offered only as proof of past performance, credentials, and industry vision | `v2_1_1_premises.public.md` |
| **Value** | The beneficiary or outcome the market is claimed to receive | At most one; never financing | same |
| **Domain** | Premises that would be revised together | For each pair: if one were wrong, would fixing it force a change to the other? If yes, same domain. When unsure, merge. Name domains in the speaker's words. Do not copy the order of the pitch | `v2_1_0_domains.public.md` |
| **Evidential status** | How the pitch supports a premise | First rule that applies: *evidence cited* (something a third party could check: own data, named customer or source, test result, demonstration; not a product description, a bare market size, a price, or a plan), *speculative* (marked uncertain), *expected* (future or plan, not marked uncertain), *asserted* (anything else). Quote the cue | `v3_0_0_links_status.md` |
| **Link** | A dependence the speaker states in so many words | Only with an explicit connective ("because", "so", "that's why", "which lets us") and a passage that holds both ends. Zero links is valid. Never infer | same |
| **Challenge** | A question from the panel that tests one condition of the theory, with the founders' response | Target a premise only if the question is about what it says; otherwise record the condition it tests. Response, first that applies: no answer, concedes, qualifies, defends, deflects | `v3_0_0_challenge.md` |

Every quoted passage must be copied exactly from the transcript. A passage that is not in the transcript is an error whatever its meaning.
