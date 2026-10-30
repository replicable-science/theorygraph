# Codebook 2.1.0 Pass C: strategic domain grouping

Pass C sorts the premises from Pass A into groups called strategic domains. The premise list is **fixed**. You may not add, remove, combine, split, rename, or reorder premises. Your only job is to put every premise into exactly one group and give each group a name.

> **Instrument note.** Sections 1 to 5 constitute the coding instrument. Sections 6 to 8 are machine only (input format, output schema, call template). Any revision to sections 1 to 5 constitutes a new codebook version; agreement statistics computed under a prior version do not carry forward.
>
> Sections 1 to 3 define the constructs and are read once during coder training. **Section 4 is the coding protocol for each premise list.** Section 5 provides three worked examples on the same hold-out cases as Pass A.


## 1. Coder role

> You are a trained research coder applying a fixed codebook to a finished list of premises from one pitch transcript. Your task is descriptive measurement, not evaluation: do not assess whether the pitch is persuasive, investable, or likely to succeed, and do not infer its outcome. Do not reconsider how the premises were split. Sort premises into groups.


## 2. Blind-coding requirement

The coding input consists of the finished premise list, transcript text for context, and an anonymous case identifier. It must not include venture name, founder name, event, year, funding history, selection outcome, or other outcome-relevant metadata.

> **Instruction to the model:** The transcript may contain a company or product name. If you recognize the venture, disregard all external knowledge of it, including subsequent funding, growth, acquisition, failure, or competitive performance. Group only the premises as given. Do not reference external knowledge in your output.


## 3. Definitions

### 3.1 Strategic domains within entrepreneurial theory

Entrepreneurial theories comprise premises that can be learned and revised together. A **strategic domain** is a set of premises that the entrepreneur would change as a bundle: fixing one would oblige a change to the others in the same group.

Premises that could be tested or revised on their own belong in **different** domains. Modularity is measured from the resulting partition.

The main coding decision in this pass is therefore **which premises would have to change together** if the theory were revised.


## 4. Coding protocol

This pass groups premises only. Do not add, remove, merge, split, or rename premises.

### 4.1 Procedure

Apply the following steps in order.

1. **Initial read.** Read the frozen premise list and transcript once without grouping.

2. **Compare premise pairs.** For each pair of premises, ask:

   > *If one of these turned out to be wrong, would fixing it force a change to the other as well?*

   Say what the change would actually be before you decide. If fixing one drags the other along, they belong in the **same** domain. If each could change while the other stayed as it is, they belong in **different** domains.

   Where the speaker links one claim to another ("because," "that's why," "this lets us," "so"), that is evidence the two would co-revise. Use these links to decide grouping only. Do not record them in your output.

3. **Form domains.** Collect premises that co-revise into groups. Assign every premise to exactly one domain. No premise is left unassigned. No premise appears in two domains.

4. **Name each domain.** Give each group a short free-text `name` drawn from the speaker's own words. Do not use category or taxonomy labels.

5. **Check presentation order.** If your groups mirror the order the speaker presented things in, or a standard business-plan outline, write in `notes` the evidence that the groups would really change separately. If you cannot point to such evidence, combine them.

6. **When the grouping is still unclear, merge.** Put the two premises in the same domain and write one line in `notes` naming the pair. Never leave a pair undecided.

**No target domain count.** Group only by the co-revision test in step 2. A domain with only one premise is fine when no other premise would have to change along with it; say why in `notes` whenever you keep one.

### 4.2 Worked examples: same domain or separate domains

The following cases apply steps 2 and 3 to recurring premise patterns. They illustrate the protocol; they do not add rules. When a case is not listed, apply steps 2 and 3 directly.

**Same domain** (one repair spills into the other):

- Problem state and the single mechanism offered to solve it when the speaker treats them as one revision: disconnected records and the unified-dashboard promise, when both would be rewritten together if the platform story failed.
- Features that share one integration path: BYOD activation, presence, and transcription from one switch platform.
- Rate opportunity and the recommendation engine that operationalizes it, when both depend on the same energy-optimization module.

**Separate domains** (each premise has its own repair):

- Product mechanism and patent protection: the technology could fail while the IP strategy stayed, or vice versa.
- Technical capability and unit economics: the product could work while margins failed.
- Yield detection and growth-cycle recovery: alerting could work while the agronomic playbook failed.
- Direct-to-consumer economics and OEM licensing: each channel could be revised independently.

Lists often raise this question. Apply the same test: if one change would address every item, the list is one domain; if each item requires its own change, split into separate domains or into single-premise domains.


## 5. Worked examples

> **Public copy.** The as-run codebook has three worked examples that quote verbatim hold-out transcripts (third-party speech). Those transcripts, and the quoted evidence spans, are withheld in this copy. The premise statements, value criteria and notes are unchanged. See `prompts/README.md` for the hashes of both files.

### 5.1 ByteKnight (`pilot-65`)


**Frozen premises:**

| Id | Premise |
|---|---|
| P1 | Cloud data centers are energy-intensive and face rising demand and cost pressure |
| P2 | Billions of idle consumer devices represent unused compute capacity |
| P3 | Distributed software can harness everyday devices for intensive compute workloads |
| P4 | Revenue sharing can incentivize device owners to join the network |
| P5 | Distributed compute can be faster and cheaper than traditional cloud for customers |
| P6 | Reusing idle devices reduces energy waste versus data centers |

**Domains:**

| Domain id | Name | Premise ids |
|---|---|
| D1 | Cloud data-center pressure | P1 |
| D2 | Idle device supply | P2 |
| D3 | Distributed compute platform | P3, P5 |
| D4 | Provider revenue sharing | P4 |
| D5 | Green energy savings | P6 |

**Notes:** P1 and P2 are separately revisable problem premises. P3 and P5 co-revise because workload orchestration and customer speed claims fail together. P4 is the supply-side incentive model. P6 is a distinct sustainability claim.

### 5.2 Pi Charging (`pilot-620`)


**Frozen premises:**

| Id | Premise |
|---|---|
| P1 | Magnetic-field charging can power multiple devices at any angle |
| P2 | A patent protects the wireless-power approach |
| P3 | The product meets FCC safety requirements for consumer use |
| P4 | Direct-to-consumer sales can sustain viable unit economics |
| P5 | Multi-room adoption extends revenue per customer |
| P6 | OEM licensing extends the platform to device manufacturers |

**Domains:**

| Domain id | Name | Premise ids |
|---|---|
| D1 | Multi-angle wireless charging | P1 |
| D2 | Patent protection | P2 |
| D3 | FCC-compliant consumer product | P3 |
| D4 | Direct-to-consumer economics | P4, P5 |
| D5 | OEM platform licensing | P6 |

**Notes:** Technology, IP, and regulatory clearance are independently revisable. P4 and P5 co-revise because margin structure and multi-room adoption are the same consumer GTM story. OEM licensing is a separate commercial path.

### 5.3 Akowe (`pilot-11`)


**Frozen premises:**

| Id | Premise |
|---|---|
| P1 | Fake academic credentials are a widespread problem |
| P2 | Institutions can issue digital credentials on blockchain |
| P3 | Employers and other third parties can verify records through the platform |
| P4 | Holders can carry verifiable credentials in a mobile app |

**Domains:**

| Domain id | Name | Premise ids |
|---|---|
| D1 | Credential fraud problem | P1 |
| D2 | Institutional digital issuance | P2 |
| D3 | Third-party verification | P3 |
| D4 | Mobile credential wallet | P4 |

**Notes:** Thin complete pitch. Each product surface is independently revisable: issuance, verification, and holder wallet would change on different fixes.


## 6. Input format (machine only)

You receive:

- The transcript (for context)
- The finished list of premises from Pass A, each with `id` and `text`

You do not receive Pass A's rules for splitting premises, and you do not need them.


## 7. Output schema (machine only)

Return exactly one JSON object. No prose outside the JSON.

**Worked example (Case 5.1 in JSON).** Domain groupings must match section 5; only the serialization format differs.

```json
{
  "meta": {"codebook_version": "2.1.0", "pass": "strategic_domains", "unit": "pitch_transcript", "case_id": "BLIND_CASE_ID", "model_id": "MODEL_ID", "model_provider": "PROVIDER", "temperature": null, "temperature_controlled": false, "extraction_run": 1, "extracted_at": "ISO-8601"},
  "domains": [
    {"id": "D1", "name": "Cloud data-center pressure", "premise_ids": ["P1"]},
    {"id": "D2", "name": "Idle device supply", "premise_ids": ["P2"]},
    {"id": "D3", "name": "Distributed compute platform", "premise_ids": ["P3", "P5"]},
    {"id": "D4", "name": "Provider revenue sharing", "premise_ids": ["P4"]},
    {"id": "D5", "name": "Green energy savings", "premise_ids": ["P6"]}
  ],
  "notes": "P3+P5 co-revise; P1, P2, P4, and P6 stand alone."
}
```

**Schema template:**

```json
{
  "meta": {
    "codebook_version": "2.1.0",
    "pass": "strategic_domains",
    "unit": "pitch_transcript",
    "case_id": "string",
    "model_id": "string",
    "model_provider": "string",
    "temperature": 0.0,
    "temperature_controlled": true,
    "extraction_run": 1,
    "extracted_at": "ISO-8601 datetime"
  },
  "domains": [
    {"id": "D1", "name": "string", "premise_ids": ["P1", "P2"]},
    {"id": "D2", "name": "string", "premise_ids": ["P3"]}
  ],
  "notes": "string"
}
```

Validity conditions:

- Every `premise_id` from the input list appears in exactly one `domains[].premise_ids`
- No `premise_id` appears in two domains
- `id` values start with `D` and are unique
- `name` is free text (no taxonomy labels)
- no `premises`, `causal_links`, `value`, `assignments`, or `quality` fields
- **provenance required:** same as Pass A


## 8. User message template (machine only)

```text
Group the frozen premises below into strategic domains using codebook v2.1.0 Pass C. Return JSON only. Do not add, remove, merge, split, or rename premises.

Requirements: premises that must be learned and revised together sit in the same domain; premises that can be tested or revised independently sit in different domains; no domain count is a target; free-text domain names drawn from the transcript; no category or taxonomy labels; every premise assigned to exactly one domain; when still unsure, merge and note the pair.

CASE_ID: {{blind_case_id}}

FROZEN PREMISES:
{{frozen_premises_with_ids_and_texts}}

TRANSCRIPT:
"""
{{transcript_raw}}
"""
```

`blind_case_id` is a random identifier held in a separate key file. Venture name, event, year, and all outcome variables are joined only after extraction is complete and locked.
