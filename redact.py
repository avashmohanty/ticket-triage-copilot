"""Strip obvious identifiers before any text goes to an LLM. Regex only: catches emails, phones, IDs, IPs.
It does NOT catch personal names or free-text secrets. Treat as one layer, not a guarantee."""
import re
PATTERNS = [("EMAIL", r"[\w.+-]+@[\w-]+\.[\w.-]+"), ("IP", r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
            ("EMPID", r"\b(?:EMP|E)\d{4,8}\b"), ("PHONE", r"(?<![\w.])\+?\(?\d[\d\s().-]{8,}\d")]
def redact(text: str) -> str:
    for tag, pat in PATTERNS:
        text = re.sub(pat, f"[{tag}]", text)
    return text

# Created by Avash Mohanty, 2026
