# Ticket Triage Copilot

LLM-assisted triage of service tickets (type, priority, tower) with PII redaction before the model call and a **confidence gate that sends uncertain tickets to a human**.

## Problem
Mis-triaged tickets are expensive: a P1 filed as P3 breaches SLA before anyone looks at it, and a ticket routed to the wrong tower loses hours in hand-offs. Keyword rules are brittle, and naive AI triage has two failure modes: sending client data to a third-party model, and confidently guessing on vague tickets ("It's not working again").

## Approach
1. **Redact first:** emails, phones, employee IDs, and IPs are stripped before any text leaves your environment.
2. **Classify** with the LLM using explicit definitions of Incident vs. Service Request and P1 to P4 (`--mode llm`), returning JSON with a confidence score and short rationale.
3. **Confidence gate:** tickets below a threshold go to human review instead of auto-routing.
4. **Control:** a keyword-rule baseline runs on the same tickets, so the AI is judged against something, not against nothing.
5. **Eval harness:** accuracy per field, P1 recall, and whether confidence actually predicts correctness.

## Run it
```bash
python data/build_data.py
python test_pipeline.py                  # offline: redaction and gate, with a faked LLM
python eval.py --mode baseline           # measured here
export ANTHROPIC_API_KEY=...             # optional: set ANTHROPIC_MODEL
python eval.py --mode llm                # fill in the table below
```
Standard library only.

## Measured result
Dataset: 30 synthetic tickets, hand-labelled.

| Metric | Keyword rules (**measured**) | LLM (`--mode llm`) |
|---|---|---|
| Type accuracy | 0.90 | _run it_ |
| Priority accuracy | 0.73 | _run it_ |
| Tower accuracy | 0.90 | _run it_ |
| All three correct | 0.67 | _run it_ |
| P1 recall | 4 of 4 | _run it_ |
| Accuracy on auto-routed tickets (gate at 0.67) | 0.64, with 28 of 30 auto-routed | _run it_ |

**What the baseline tells you:** one ticket in three gets at least one field wrong, mostly priority. The rules' own confidence is useless as a gate: 93% of tickets pass it, yet accuracy among them is only 64%. With an LLM you need to check that its confidence is any better, and `eval.py` reports exactly that. LLMs' self-reported confidence is often poorly calibrated, so treat that as a hypothesis to test, not a feature to assume.

Redaction: 10 of 10 synthetic identifiers caught in the offline test. The test originally caught two defects (IPs mislabelled as phone numbers, a stray bracket on one phone format), both fixed.

**The LLM column is empty on purpose.** No API key was available when this was built, so I did not publish an unmeasured number.

## Limitations
- 30 hand-written tickets, labelled by one person. Priority is partly subjective, so some "misses" are arguable. Use your own historical tickets and your own priority matrix.
- Regex redaction does not catch personal names or secrets in free text. Treat it as one layer, not a guarantee.
- Do not auto-route P1 on model output alone without a fast human confirmation path.
- Check your organisation's AI and data-handling policy before sending any real ticket text to an external model.

Created by Avash Mohanty, 2026
