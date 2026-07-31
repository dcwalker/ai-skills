#!/usr/bin/env python3
"""Cross-skill eval report: one table over every committed benchmark baseline.

Walks plugins/*/skills/*/evals/benchmark-baseline.json and prints a markdown
table of each skill's eval count, expectation totals, pass rate, and baseline
date, plus repo-wide totals. Read-only; the committed baselines stay the
single source of truth (see each skill's benchmark-baseline.md for per-eval
detail and narrative notes).

Usage, from the repo root:
    python3 evals/lib/report.py
"""

import glob
import json
import sys


def main() -> int:
    paths = sorted(glob.glob("plugins/*/skills/*/evals/benchmark-baseline.json"))
    if not paths:
        print("No benchmark-baseline.json files found; run from the repo root.", file=sys.stderr)
        return 1

    rows = []
    for path in paths:
        with open(path) as f:
            d = json.load(f)
        skill = d.get("metadata", {}).get("skill_name") or path.split("/skills/")[1].split("/")[0]
        plugin = path.split("plugins/")[1].split("/")[0]
        date = (d.get("metadata", {}).get("timestamp") or "?")[:10]
        runs = d.get("runs", [])
        # Aggregate per eval_id, not per run: a baseline may hold multiple
        # runs of the same eval (run_number / runs_per_configuration), and an
        # eval only counts as fully passing when every one of its runs passed
        # every expectation. Integer passed/total comparison also avoids
        # float equality on pass_rate.
        evals = {}
        for r in runs:
            res = r["result"]
            agg = evals.setdefault(r["eval_id"], {"passed": 0, "total": 0})
            agg["passed"] += res.get("passed", 0)
            agg["total"] += res.get("total", 0)
        n_evals = len(evals)
        passed = sum(a["passed"] for a in evals.values())
        total = sum(a["total"] for a in evals.values())
        fully_passing = sum(1 for a in evals.values()
                            if a["total"] > 0 and a["passed"] == a["total"])
        rate = (passed / total * 100) if total else 0.0
        rows.append((skill, plugin, n_evals, fully_passing, passed, total, rate, date))

    rows.sort(key=lambda r: (r[6], r[0]))

    print("| Skill | Plugin | Evals | Evals at 100% | Expectations | Pass rate | Baseline date |")
    print("|-------|--------|------:|--------------:|-------------:|----------:|---------------|")
    for skill, plugin, n_evals, fully, passed, total, rate, date in rows:
        print(f"| {skill} | {plugin} | {n_evals} | {fully}/{n_evals} | {passed}/{total} | {rate:.1f}% | {date} |")

    g_evals = sum(r[2] for r in rows)
    g_full = sum(r[3] for r in rows)
    g_passed = sum(r[4] for r in rows)
    g_total = sum(r[5] for r in rows)
    g_rate = (g_passed / g_total * 100) if g_total else 0.0
    print(f"| **Total ({len(rows)} skills)** | | **{g_evals}** | **{g_full}/{g_evals}** | "
          f"**{g_passed}/{g_total}** | **{g_rate:.1f}%** | |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
