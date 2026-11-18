"""Minimal Anthropic Messages API client (stdlib only) + tolerant JSON parsing."""
import json, os, re, urllib.request

API = "https://api.anthropic.com/v1/messages"

def complete(system: str, user: str, model: str | None = None, max_tokens: int = 2000) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("Set ANTHROPIC_API_KEY to use --mode llm")
    model = model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")  # override with any current model
    body = json.dumps({"model": model, "max_tokens": max_tokens, "temperature": 0, "system": system,
                       "messages": [{"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(API, body, {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.load(r)
    return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")

def parse_json(text: str):
    """Accept raw JSON or JSON wrapped in prose / code fences."""
    text = re.sub(r"```(?:json)?", "", text).strip()
    pairs = [(text.find(o), o, c) for o, c in (("[", "]"), ("{", "}")) if text.find(o) != -1]
    for i, _, closer in sorted(pairs):  # outermost structure = whichever opens first
        j = text.rfind(closer)
        if j > i:
            try:
                return json.loads(text[i:j + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("No valid JSON found in model output")

# Created by Avash Mohanty, 2026
