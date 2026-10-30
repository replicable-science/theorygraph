# Codebook 3.0.0 Pass E: challenge in the question-and-answer session

Pass E reads the question-and-answer (Q&A) session that follows a pitch and records **which premises the questioners tested and how the founders responded**. It uses the premise list from Pass A and does not change it. It does not judge whether the founders' answers were good.

> **Instrument note.** Sections 1 to 4 are the coding instrument. Section 5 is a worked example on a fictional session. Section 6 is machine only.

## 1. Coder role

You are a trained research coder. You describe who asked what and what was answered. You do not judge who was right, and you do not use outside knowledge about the venture. The transcript has no speaker labels: infer who is questioning and who is answering from the content (questions come from the panel; answers come from the founders). If you cannot tell, skip the passage.

## 2. What counts as an exchange

An **exchange** is a question or objection from the panel that tests a specific condition of the venture's theory, together with the founders' response to it.

Count it when the question asks whether, why, or how a condition would hold: *how will you get customers, what stops a competitor, why would they pay, does it work at scale.*

Do not count: greetings and thanks, praise with no question, requests to repeat or clarify what was said, and questions about financing, valuation, or the founder's biography, unless the question tests a condition that is in the premise list.

Group a question and its immediate follow-ups on the same condition into **one** exchange.

## 3. Coding each exchange

- `targets`: the ids of the frozen premises the question tests (one or two). Choose a premise only if the question is about what that premise says. Do **not** pick the nearest premise. If no premise fits, use `[]` and write the condition the question tests in `new_condition` (at most twelve words); otherwise `new_condition` is empty. A question about competitors or copying is a condition that is often missing from the list.
- `question_span`: the shortest passage that holds the question, copied exactly from the Q&A transcript.
- `answer_span`: the shortest passage that holds the core of the response, copied exactly from the Q&A transcript. Empty only when `response` is `no_answer`.
- `response`: choose the **first** that applies.
  1. `no_answer`: the transcript shows no response to the question.
  2. `concedes`: the founders accept that the condition may not hold or say they would change course.
  3. `qualifies`: the founders keep the claim but narrow it (one segment, one region, a later stage, a condition).
  4. `defends`: the founders answer the question and keep the claim as stated, giving a reason or an example.
  5. `deflects`: the founders respond but to a different question, or restate the vision without addressing the condition.

## 4. What this pass does not do

- It does not score the quality of an answer.
- It does not attribute remarks to named individuals.
- It does not add premises to the pitch's list. New conditions are recorded only in `new_condition`.

## 5. Worked example (fictional session)

**Premises:** P1 "A paper label read by a phone camera lets workers find pallets in seconds"; P2 "Warehouses will pay six dollars per worker per month"; P3 "Forklift leasing companies are an effective sales channel".

**Q&A transcript:** "Why would a warehouse pay six dollars a head, when the paper label costs ten cents and the work is mostly done by the camera? We think the saving is about twelve dollars of lost time per worker per month, so six is half of that. Okay. And what happens if the lighting in a depot is bad, can the phone still read the label? In the test depot it was minus eighteen degrees and dim, and it read ninety six percent of labels. Why would a leasing company help you sell instead of building this themselves? Honestly we are not sure they will. We may have to hire our own sales team."

**Coding**

| Id | Targets | Question span | Answer span | Response |
|---|---|---|---|---|
| Q1 | P2 | "Why would a warehouse pay six dollars a head" | "the saving is about twelve dollars of lost time per worker per month, so six is half of that" | defends |
| Q2 | P1 | "what happens if the lighting in a depot is bad" | "it was minus eighteen degrees and dim, and it read ninety six percent of labels" | defends |
| Q3 | P3 | "Why would a leasing company help you sell" | "we are not sure they will. We may have to hire our own sales team" | concedes |

## 6. Output schema (machine only)

Return exactly one JSON object. No prose outside the JSON.

```json
{
  "meta": {"codebook_version": "3.0.0", "pass": "challenge", "unit": "qa_transcript", "case_id": "string", "model_id": "string", "extraction_run": 1},
  "exchanges": [
    {"id": "Q1", "targets": ["P2"], "new_condition": "", "question_span": "verbatim Q&A substring", "answer_span": "verbatim Q&A substring", "response": "defends"}
  ],
  "notes": "string"
}
```

Validity conditions:

- `response` is one of `defends`, `qualifies`, `concedes`, `deflects`, `no_answer`
- every id in `targets` is in the frozen list; `targets` is empty only when `new_condition` is not
- `question_span` and `answer_span` are verbatim substrings of the Q&A transcript; `answer_span` is empty only for `no_answer`
- `exchanges` may be empty
