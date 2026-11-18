"""Score triage against gold labels. Usage: python eval.py --mode baseline|llm [--threshold 0.67]"""
import argparse, csv
from triage import baseline, llm_triage, route

def run(mode, thr):
    rows = list(csv.DictReader(open("data/tickets.csv")))
    n = len(rows); ok = {"type": 0, "priority": 0, "tower": 0, "all": 0}; p1_tp = p1_fp = p1_fn = 0; auto = auto_ok = 0; bad = []
    for r in rows:
        res = baseline(r["title"], r["description"]) if mode == "baseline" else llm_triage(r["title"], r["description"])
        c = {k: res[k] == r[k] for k in ("type", "priority", "tower")}
        for k in c: ok[k] += c[k]
        ok["all"] += all(c.values())
        if res["priority"] == "P1" and r["priority"] == "P1": p1_tp += 1
        elif res["priority"] == "P1": p1_fp += 1
        elif r["priority"] == "P1": p1_fn += 1
        if route(res, thr) == "auto":
            auto += 1; auto_ok += all(c.values())
        if not all(c.values()): bad.append((r["id"], r["title"][:38], {k: (res[k], r[k]) for k in c if not c[k]}))
    print(f"mode={mode} n={n}")
    print(f"accuracy: type={ok['type']/n:.2f} priority={ok['priority']/n:.2f} tower={ok['tower']/n:.2f} all-three={ok['all']/n:.2f}")
    print(f"P1 recall={p1_tp}/{p1_tp+p1_fn}  P1 false alarms={p1_fp}")
    print(f"confidence gate @{thr}: auto-routed {auto}/{n} ({auto/n:.0%}), all-three accuracy on auto-routed = {auto_ok}/{auto}" + (f" = {auto_ok/auto:.2f}" if auto else ""))
    for b in bad[:12]: print("  miss", *b)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["baseline", "llm"], default="baseline")
    ap.add_argument("--threshold", type=float, default=0.67); a = ap.parse_args(); run(a.mode, a.threshold)

# Created by Avash Mohanty, 2026
