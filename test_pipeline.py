"""Offline tests: redaction, JSON parsing, confidence gate, and that PII never reaches the (faked) LLM."""
import triage
from redact import redact

cases = ["mail jo.smith@corp.com now", "call +91 98765 43210 please", "EMP204455 is locked", "host 10.20.30.40 down",
         "ring (212) 555-0182", "contact a_b-c@sub.example.org", "ID E123456", "ip 192.168.1.1", "tel 020 7946 0958", "x@y.io"]
tags = ["[EMAIL]", "[PHONE]", "[EMPID]", "[IP]", "[PHONE]", "[EMAIL]", "[EMPID]", "[IP]", "[PHONE]", "[EMAIL]"]
caught = sum(t in redact(c) for c, t in zip(cases, tags))
print(f"redaction: {caught}/{len(cases)} synthetic identifiers caught"); assert caught == len(cases)

seen = {}
def fake(system, user, **k):
    seen["user"] = user
    return 'Sure!\n{"type":"Incident","priority":"P2","tower":"Access & Identity","confidence":"0.4","rationale":"vague"}'
triage.complete = fake
r = triage.llm_triage("Login broken", "mail jo.smith@corp.com or call +91 98765 43210")
assert "jo.smith" not in seen["user"] and "98765" not in seen["user"], seen
assert r["confidence"] == 0.4 and triage.route(r) == "human_review"
assert triage.route({"confidence": 0.9}) == "auto"
print("PASS: PII stripped before LLM call, tolerant JSON parse, low confidence routed to human")

# Created by Avash Mohanty, 2026
