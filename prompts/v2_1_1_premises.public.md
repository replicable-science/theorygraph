# Codebook 2.1.1 Pass A: premise extraction

Pass A extracts the premises of an entrepreneurial theory from a single pitch transcript. Strategic domains and causal links are not coded in this pass. Pass B (composition tagging) and Pass C (domain grouping) are applied subsequently to the finalized premise list.

> **Instrument note.** Sections 1 to 5 constitute the coding instrument. Sections 6 and 7 are machine only (output format and call template). Any revision to sections 1 to 5 constitutes a new codebook version; agreement statistics computed under a prior version do not carry forward.
>
> Sections 1 to 3 define the constructs and are read once during coder training. **Section 4 is the coding protocol for each transcript.** Section 5 provides three worked examples.


## 1. Coder role

> You are a trained research coder applying a fixed codebook to a single pitch transcript. Your task is descriptive measurement, not evaluation: do not assess whether the pitch is persuasive, investable, or likely to succeed, and do not infer its outcome. Code only what the transcript states or clearly implies. Where the text does not support a coding decision, omit the unit rather than inferring structure.


## 2. Blind-coding requirement

The coding input consists of transcript text and an anonymous case identifier. It must not include venture name, founder name, event, year, funding history, selection outcome, or other outcome-relevant metadata.

> **Instruction to the model:** The transcript may contain a company or product name. If you recognize the venture, disregard all external knowledge of it, including subsequent funding, growth, acquisition, failure, or competitive performance. Code only what this transcript claims. Do not reference external knowledge in your output.


## 3. Definitions

### 3.1 Premises within entrepreneurial theory

Entrepreneurial theories comprise three elements: (1) **premises** about conditions that drive value creation, (2) **causal links** connecting premises to one another and to value, and (3) **strategic domains** grouping premises that can be learned and revised together. This codebook codes the first element only.

### 3.2 Premise

A **premise** is an explicit or clearly implied claim about a condition the entrepreneur treats as necessary for the theory to create value. The claim must be specific enough that, in principle, it could be shown to be wrong.

Breadth is measured as the count of premises. The main coding decision in this pass is therefore **how to split the transcript into premises**: where one premise ends and the next begins.


## 4. Coding protocol

This pass extracts premises only. Composition tagging and domain grouping are deferred to later passes.

### 4.1 Procedure

Apply the following steps in order.

1. **Initial read.** Read the transcript once without coding.

2. **Identify claims.** Mark each claim the entrepreneur presents as necessary for the venture's theory of value to hold. Claims may take the form of design choices, capabilities, or assumptions about customers, channels, technology, or operations. Code each claim at the scope at which the entrepreneur asserts it: do not subdivide a claim the entrepreneur did not separate, and do not merge claims the entrepreneur kept distinct. When the entrepreneur bundles several items into one assertion (e.g., "parents face five pain points"), treat the whole assertion as one claim.

3. **Apply exclusions.** Do not code the following as premises:

   - Financing ask, valuation, equity offered, or capital already raised.
   - Greetings, closings, thanks, and appeals to the audience.
   - Speech by anyone other than the pitching entrepreneur(s), and any Q&A content.
   - Product or company name stated without an associated condition.
   - Biographical credentials, unless the theory itself would have to change if the credential were untrue, rather than merely looking weaker.
   - Traction or press metrics offered as evidence of past performance. When the entrepreneur presents the underlying mechanism as a continuing condition for value, code the mechanism, not the metric.
   - Industry vision statements (e.g., *"the future of data is a writable future"*). See section 4.3.

4. **State what would need to change.** For each remaining claim, write briefly what the entrepreneur would need to change if the claim turned out to be wrong (e.g., *reformulate the product*, *secure alternative supply*, *rebuild the tracking module*). If nothing would need to change, the claim is not a condition the venture depends on; exclude it.

   Write the change as **work the venture would have to carry out**, at the scale at which it would actually carry it out — the examples above are the intended scale. A change that the venture would complete *in the course of* carrying out another change you have already written is not a separate change: adding one more screen, field, integration, or notification inside a capability already listed is part of building that capability, not work of its own. Where the entrepreneur states or shows that an item was built separately, or could be dropped while the rest stood, it is work of its own.

5. **Decide how many premises.** Claims that would require the same change belong to **one premise**. Claims that would require different changes belong to **separate premises**.

6. **When the split is still unclear, record separate premises.** Reach this step only after writing the changes in step 4 and comparing them in step 5; it settles cases those steps leave open, and is not an alternative to performing them. Name the undecided pair and both changes you wrote in `notes`. Do not default to merging.

7. **Record each premise.** State each premise as one declarative sentence in the entrepreneur's terms, normalized only for grammar. Attach an **evidence span**: a contiguous substring copied verbatim from the transcript. Spacing and capitalization may differ from the premise text; the words must match. Do not paraphrase or quote text absent from the transcript. Where the meaning is clear despite an obvious transcription error, correct the premise text only; the evidence span retains the transcript as written. If the transcript is truncated, code only what is present. When multiple co-founders present, pool their claims without duplicating premises stated by more than one speaker.

**No target premise count.** Breadth is computed downstream and is not a coding input. Neither narrow nor broad theories are preferred; do not add, omit, or merge premises to adjust list length.

### 4.2 Worked examples: one premise or several

The following cases apply steps 4 and 5 to recurring transcript patterns. They illustrate the protocol; they do not add rules. When a case is not listed, apply steps 4 and 5 directly.

**One premise** (one change would address all claims):

- Restatement or near-synonyms: *"it's delicious, it tastes great, people love the flavor."*
- Quantitative detail modifying a claim: *"24 inches tall, holds 26 ounces."*
- A mechanism presented as indivisible: *"a single 30-second phone scan replaces in-person measurement."*
- Performance attributes of one process: *"faster, cheaper, uses less water, emits less CO2."*
- Enumerated applications of one capability: *"First, active warning. Two, usable for logistics. Three, your building has a Carfax,"* describing one sensor network.
- Features that follow from a single integration, such as BYOD activation, presence, and transcription from one switch platform.
- Price and channel structure for the same offering.
- Patents attached to a mechanism already claimed.
- A problem set presented as one unmet need: *"parents face five major pain points."*
- Steps of a live demonstration that show one capability in use: opening a card, seeing nearby showtimes, following a link into another app, receiving a notification — one integrated product being shown from several angles.

**Several premises** (each claim requires its own change):

- Coordinated claims about different conditions: *"combines seaweed and mushrooms, and we source kelp from regenerative ocean farms."*
- Capabilities each performing a distinct function: communication, report cards, GPS tracking, fee payment, delivery.
- Intellectual property licensed or sold as a separate line of business.
- A product use presented as independently offered.
- Partner or reseller economics that could fail while the stated price point remained.
- Demonstrated steps the entrepreneur presents as built or sold separately, such as a module offered on its own or one the pitch says could be dropped while the rest stood.

Lists often raise this question and appear on both sides above. Apply the same test: if one change would address every item, the list is one premise; if each item requires its own change, each is a separate premise. In the School Bridge pitch, five pain points form one premise (change: re-target the problem set); five product capabilities form five premises (each requires its own build or change).

Product demonstrations raise it in the same way and are settled the same way, using the scale of change set in step 4: a walkthrough that moves through one product does not become several premises because it has several moments, and a walkthrough does not become one premise because it was shown in one sitting. Ask what work each shown step would be, and whether that work would be done as part of building a step already recorded.

### 4.3 Value criterion

Record **one value criterion** in the `value` field: the beneficiary and/or the outcome the market is claimed to receive. When the entrepreneur identifies a priority benefit, code that benefit. Financing is never a value criterion.

Omit `value` only when the transcript neither states nor clearly implies a value criterion, as when a pitch is truncated before value is asserted. Do not infer a value criterion.

The value criterion is not an independent variable in the analysis. It anchors what counts as "necessary for the theory to create value" and permits audit of premise coding decisions.


## 5. Worked examples

> **Public copy.** The as-run codebook has three worked examples that quote verbatim hold-out transcripts (third-party speech). Those transcripts, and the quoted evidence spans, are withheld in this copy. The premise statements, value criteria and notes are unchanged. See `prompts/README.md` for the hashes of both files.

### 5.1 ByteKnight (`pilot-65`)


**Premises:**

| Id | Premise |
|---|---|
| P1 | Cloud data centers are energy-intensive and face rising demand and cost pressure |
| P2 | Billions of idle consumer devices represent unused compute capacity |
| P3 | Distributed software can harness everyday devices for intensive compute workloads |
| P4 | Revenue sharing can incentivize device owners to join the network |
| P5 | Distributed compute can be faster and cheaper than traditional cloud for customers |
| P6 | Reusing idle devices reduces energy waste versus data centers |

**Value criterion:** Computing becomes sustainable and equitable through a distributed device grid.

**Notes:** Semiconductor shortage and AI demand illustrate P1; they are not separate premises. Beta status, wait list, and Storj partnership are excluded as traction under step 3.

### 5.2 Pi Charging (`pilot-620`)


**Premises:**

| Id | Premise |
|---|---|
| P1 | Magnetic-field charging can power multiple devices at any angle |
| P2 | A patent protects the wireless-power approach |
| P3 | The product meets FCC safety requirements for consumer use |
| P4 | Direct-to-consumer sales can sustain viable unit economics |
| P5 | Multi-room adoption extends revenue per customer |
| P6 | OEM licensing extends the platform to device manufacturers |

**Value criterion:** Consumers get safe, affordable contactless charging without charging pads.

**Notes:** Reservation counts, press coverage, and investor names elsewhere in the full pitch are excluded as traction. Patent protection and FCC compliance are separate premises because each would require a different change if wrong.

### 5.3 Akowe (`pilot-11`)


**Premises:**

| Id | Premise |
|---|---|
| P1 | Fake academic credentials are a widespread problem |
| P2 | Institutions can issue digital credentials on blockchain |
| P3 | Employers and other third parties can verify records through the platform |
| P4 | Holders can carry verifiable credentials in a mobile app |

**Value criterion:** Academic credentials are issued and carried safely and verifiably.

**Notes:** API issuance extends the institutional channel and is not a separate premise. Corporate customer count, fundraising, booth location, and demo offer are excluded under step 3.


## 6. Output schema (machine only)

Return exactly one JSON object. No prose outside the JSON.

**Worked example (Case 5.1 in JSON).** Premise and value content must match section 5; only the serialization format differs.

```json
{
  "meta": {"codebook_version": "2.1.1", "pass": "premises", "unit": "pitch_transcript", "case_id": "BLIND_CASE_ID", "model_id": "MODEL_ID", "model_provider": "PROVIDER", "temperature": null, "temperature_controlled": false, "extraction_run": 1, "extracted_at": "ISO-8601"},
  "premises": [
    {"id": "P1", "text": "Cloud data centers are energy-intensive and face rising demand and cost pressure", "status": "explicit", "evidence_span": "<verbatim transcript substring>"},
    {"id": "P2", "text": "Billions of idle consumer devices represent unused compute capacity", "status": "explicit", "evidence_span": "<verbatim transcript substring>"},
    {"id": "P3", "text": "Distributed software can harness everyday devices for intensive compute workloads", "status": "explicit", "evidence_span": "<verbatim transcript substring>"},
    {"id": "P4", "text": "Revenue sharing can incentivize device owners to join the network", "status": "explicit", "evidence_span": "<verbatim transcript substring>"},
    {"id": "P5", "text": "Distributed compute can be faster and cheaper than traditional cloud for customers", "status": "explicit", "evidence_span": "<verbatim transcript substring>"},
    {"id": "P6", "text": "Reusing idle devices reduces energy waste versus data centers", "status": "explicit", "evidence_span": "<verbatim transcript substring>"}
  ],
  "value": [
    {"id": "V1", "text": "Computing becomes sustainable and equitable through a distributed device grid", "status": "explicit", "evidence_span": "<verbatim transcript substring>"}
  ],
  "notes": "Beta, wait list, and Storj partnership excluded as traction."
}
```

**Schema template:**

```json
{
  "meta": {
    "codebook_version": "2.1.1",
    "pass": "premises",
    "unit": "pitch_transcript",
    "case_id": "string",
    "model_id": "string",
    "model_provider": "string",
    "temperature": 0.0,
    "temperature_controlled": true,
    "extraction_run": 1,
    "extracted_at": "ISO-8601 datetime"
  },
  "premises": [
    {"id": "P1", "text": "string", "status": "explicit|inferred", "evidence_span": "<verbatim transcript substring>"}
  ],
  "value": [
    {"id": "V1", "text": "string", "status": "explicit|inferred", "evidence_span": "<verbatim transcript substring>"}
  ],
  "notes": "string"
}
```

Validity conditions:

- `premises` is non-empty
- `value` has **exactly one** item if present; do not include a `secondary_value` field
- no `domains`, `causal_links`, `taxonomy`, `epistemic_markers`, or `quality` fields
- ids unique; `P*` premises, `V*` value
- every `evidence_span` verifies as a verbatim transcript substring
- **provenance required:** `meta.model_id` (non-empty string) and `meta.temperature_controlled` (boolean). `meta.temperature` carries a number only when sampling was actually pinned; when the extraction ran through a harness that does not expose the parameter, set `temperature_controlled: false` and `temperature: null` rather than recording an intended value as though it had been enforced. Record `model_provider`, `extraction_run`, and `extracted_at` whenever available.


## 7. User message template (machine only)

```text
Extract the critical premises of the entrepreneurial theory from the transcript below using codebook v2.1.1 Pass A. Return JSON only. Do not use any outside knowledge about this venture.

Requirements: record separate premises when each claim would require a different change, and one premise when a single change would suffice; no target premise count; no domains or causal links in this pass; every evidence_span copied verbatim from the transcript. When the entrepreneur states a value criterion, record exactly one value node.

CASE_ID: {{blind_case_id}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```

`blind_case_id` is a random identifier held in a separate key file. Venture name, event, year, and all outcome variables are joined only after extraction is complete and locked.
