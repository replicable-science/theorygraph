# Codebook 3.0.0 Pass D: evidential status and links

Pass D adds two things to a premise list that already exists (Pass A): **how each premise is supported in the pitch** (its evidential status) and **which premises the speaker explicitly connects**. It does not add, remove, merge, split or rename premises, and it does not judge whether a claim is true.

> **Instrument note.** Sections 1 to 4 are the coding instrument. Section 5 is a worked example on a fictional pitch. Section 6 is machine only. Any change to sections 1 to 4 is a new codebook version.

## 1. Coder role

You are a trained research coder. You describe what a speaker says and how the speaker says it. You do not judge whether the pitch is persuasive, investable, or true, and you do not use outside knowledge about the venture. If the transcript does not support a decision, choose the more cautious option below.

## 2. Evidential status of a premise

Give every frozen premise exactly one status. Decide by taking the **first** rule that applies, in this order.

1. `evidence_cited`: in the transcript the speaker supports this premise with something specific that a third party could check: a number from the venture's own data, a named customer or partner, a pilot or test result, a named outside source, or a demonstration shown during the pitch. The following do **not** count as evidence: describing what the product is or does, a market size or growth rate with no source, a price, and the speaker's own plans or credentials.
2. `speculative`: the speaker marks the claim as uncertain: *might, could, may, hope, believe, we think, we guess, if, potentially, probably*.
3. `expected`: the claim is about the future or is a plan, and is not marked as uncertain: *we will, we plan to, we are going to, soon, next year, this will let us*.
4. `asserted`: the speaker states the claim as a fact, with no support and no marker of uncertainty.

For `evidence_cited`, `speculative` and `expected`, copy into `status_span` the shortest passage of the transcript that shows the status, exactly as written (a contiguous substring). For `asserted`, leave `status_span` empty. Add a `status_reason` of at most twelve words.

If two rules seem to apply, take the earlier one. If you cannot decide between `asserted` and anything else, choose `asserted`.

## 3. Links between premises

A **link** is a dependence the speaker states themselves: one condition is named as the reason for, or the means to, another condition or the value.

Record a link only when both of these hold:

- the speaker connects the two with explicit language such as *because, so, that's why, which lets us, which means, therefore, as a result, in order to, thanks to*. Words such as *and, on, with*, or a bare *which*, are not connectives; and
- you can copy one contiguous passage of the transcript that contains the connection.

Do not infer links from topic, from the order of the pitch, or from your own idea of how a business works. Most pitches state few links. **Zero links is a valid answer.**

Direction: `from` is the reason or means the speaker gives, `to` is what it is given as a reason or means for. `to` may be a premise id or the value id `V1`. Do not link a premise to itself. Record the connective words in `cue`.

## 4. What this pass does not do

- It does not add premises. If the speaker states a dependence on something that is not in the frozen list, leave it out.
- It does not rate the strength, importance or probability of any claim.
- It does not use anything the speaker did not say.

## 5. Worked example (fictional pitch)

**Transcript:** "Dock workers lose about a fifth of their shift looking for the right pallet. We tag every pallet with a ten cent paper label, and our app reads the labels from a phone camera, so a worker finds a pallet in seconds. In a three week test at a cold storage depot in Rotterdam, search time dropped from nineteen minutes an hour to four. We think warehouses will pay six dollars per worker per month for that. We will sell through the forklift leasing companies, because they already visit every warehouse every quarter."

**Frozen premises**

| Id | Premise |
|---|---|
| P1 | Dock workers lose a large share of their shift searching for pallets |
| P2 | A paper label read by a phone camera lets workers find pallets in seconds |
| P3 | Warehouses will pay six dollars per worker per month |
| P4 | Forklift leasing companies are an effective sales channel |
| P5 | Forklift leasing companies already visit every warehouse every quarter |

**Value:** V1, workers spend their shift moving goods, not searching.

**Coding**

| Id | Status | Status span | Reason |
|---|---|---|---|
| P1 | asserted | | Stated as fact, no source |
| P2 | evidence_cited | "In a three week test at a cold storage depot in Rotterdam, search time dropped from nineteen minutes an hour to four" | Own test with numbers |
| P3 | speculative | "We think warehouses will pay six dollars per worker per month" | Marked with "we think" |
| P4 | expected | "We will sell through the forklift leasing companies" | Plan, no marker of doubt |
| P5 | asserted | | Stated as fact, no source |

**Links:** one link. The speaker gives the visits as the reason for the channel ("because they already visit every warehouse every quarter"), so record `P5` → `P4` with cue `because` and the passage "We will sell through the forklift leasing companies, because they already visit every warehouse every quarter". No other connection is stated, so no other link is recorded.

## 6. Output schema (machine only)

Return exactly one JSON object. No prose outside the JSON.

```json
{
  "meta": {"codebook_version": "3.0.0", "pass": "links_status", "unit": "pitch_transcript", "case_id": "string", "model_id": "string", "extraction_run": 1},
  "premises": [
    {"id": "P1", "status": "asserted", "status_span": "", "status_reason": "Stated as fact, no source"},
    {"id": "P2", "status": "evidence_cited", "status_span": "verbatim transcript substring", "status_reason": "Own test with numbers"}
  ],
  "links": [
    {"id": "L1", "from": "P2", "to": "V1", "cue": "so", "evidence_span": "verbatim transcript substring"}
  ],
  "notes": "string"
}
```

Validity conditions:

- every frozen premise id appears exactly once in `premises`, and no other id appears
- `status` is one of `evidence_cited`, `speculative`, `expected`, `asserted`
- `status_span` is a verbatim substring of the transcript for every status except `asserted`
- `from` and `to` name ids in the frozen list or the value id; `from` is a premise id; no self links
- every `evidence_span` is a verbatim substring of the transcript
- `links` may be empty
