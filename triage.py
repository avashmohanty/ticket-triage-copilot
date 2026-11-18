"""Ticket triage: classify type, priority, tower, with a confidence gate that routes low-confidence tickets to a human."""
import re
from llm import complete, parse_json
from redact import redact

TOWERS = ["Applications", "Infrastructure", "Data & Reporting", "Access & Identity"]

# ---------- baseline (keyword rules) ----------
def baseline(title, desc):
    t = f"{title} {desc}".lower(); hits = 0
    if re.search(r"\b(error|down|not working|cannot|can't|fail|failed|failing|outage|slow|crash|broken|offline|unreachable|stuck|wrong|not arriving|disconnect)", t):
        typ = "Incident"; hits += 1
    elif re.search(r"\b(please|request|need|create|provision|install|add|extend|rotate|could you|how do i|where is)", t):
        typ = "Service Request"; hits += 1
    else:
        typ = "Service Request"
    if re.search(r"\b(prod|production)\b.*\b(not|error|fail|down)|all (users|customers)|total|outage|regulat", t): pr = "P1"; hits += 1
    elif re.search(r"\b(several|team|\d{2,} people|around \d+|all .*agents|stale|contractors)", t) and typ == "Incident": pr = "P2"; hits += 1
    elif typ == "Service Request": pr = "P4" if re.search(r"\b(add|reset|rotate|how do i|where is|extract)", t) else "P3"; hits += 1
    else: pr = "P3"
    for tower, pat in [("Access & Identity", r"\b(access|password|login|sso|mfa|permission|mailing list|role)"),
                       ("Data & Reporting", r"\b(report|dashboard|etl|extract|power ?bi|data|rows|figures)"),
                       ("Infrastructure", r"\b(server|vpn|network|database|db|disk|storage|printer|environment|build agent|data center)")]:
        if re.search(pat, t): tw = tower; hits += 1; break
    else: tw = "Applications"
    return {"type": typ, "priority": pr, "tower": tw, "confidence": round(hits / 3, 2), "rationale": "keyword rules"}

# ---------- LLM ----------
SYSTEM = f"""You triage IT service tickets for a managed-services team.
Return ONLY one JSON object: {{"type":"Incident|Service Request","priority":"P1|P2|P3|P4","tower":"{'|'.join(TOWERS)}","confidence":0.0-1.0,"rationale":"<=25 words"}}.
Definitions: Incident = something that worked and is now broken or degraded. Service Request = a standard ask (access, install, report, question, enhancement).
P1 = production down, data integrity or regulatory impact, or all users affected. P2 = major degradation or a group of users blocked, workaround may exist.
P3 = single user or minor degradation. P4 = routine request, cosmetic or question.
Use ONLY the ticket text. If the ticket is vague, lower the confidence below 0.5 rather than guessing."""

def llm_triage(title, desc):
    r = parse_json(complete(SYSTEM, redact(f"Title: {title}\nDescription: {desc}"), max_tokens=300))
    r["confidence"] = float(r.get("confidence", 0))
    return r

def route(result, threshold=0.67):
    return "auto" if result["confidence"] >= threshold else "human_review"

# Created by Avash Mohanty, 2026
