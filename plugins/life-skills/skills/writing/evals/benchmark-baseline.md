# Skill Benchmark: writing

**Model**: claude-sonnet-5 (executor), claude-opus-5 (analyzer)
**Date**: 2026-08-24
**Evals**: 1-27 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectation Pass Rate | 142/142 (100%) |
| Evals Fully Passed | 27/27 |
| Time | 115.7s ± 50.4s |
| Output Tokens | 9542 ± 4037 |
| Errors | 0 |
| Skill invoked | 27/27 trials |

Supersedes 141/142 (2026-08-24), 138/142 (2026-08-23), and 106/111 across the
older 22-eval suite (2026-08-13).

## Per-eval results

| Eval | Scenario | Pass Rate | Time (s) | Tokens |
|------|----------|-----------|----------|--------|
| 1 | Peer email, rung-1 corpus | 6/6 | 115.5 | 8941 |
| 2 | New external recipient, rung-2 substitution | 5/5 | 151.8 | 12937 |
| 3 | No corpus anywhere | 5/5 | 30.3 | 2056 |
| 4 | Audience missing from the request | 4/4 | 6.2 | 310 |
| 5 | Two artifacts, two audiences, one run | 5/5 | 196.0 | 17643 |
| 6 | Rewrite an assistant-sounding draft | 4/4 | 111.3 | 9524 |
| 7 | Explicit skip-the-research override | 4/4 | 26.8 | 2015 |
| 8 | Journal entry, audience is self | 4/4 | 139.3 | 11389 |
| 9 | Voice held across two revisions | 5/5 | 105.7 | 9030 |
| 10 | Cache belonging to different accounts | 4/4 | 129.8 | 11192 |
| 11 | Own cache reused and confirmed | 4/4 | 76.0 | 6355 |
| 12 | Blog post from posts on disk | 5/5 | 181.1 | 15733 |
| 13 | Jira comment, display-name collision | 5/5 | 116.4 | 9794 |
| 14 | Slack corpus from an on-disk export | 6/6 | 152.6 | 12733 |
| 15 | General-profile fallback, personal audience | 6/6 | 78.1 | 5992 |
| 16 | Slack corpus through the connector | 6/6 | 124.1 | 10754 |
| 17 | Two-sample corpus, confidence calibration | 5/5 | 117.1 | 9366 |
| 18 | Register mismatch, banter corpus, serious news | 5/5 | 101.4 | 8300 |
| 19 | Revision pushing against the observed voice | 5/5 | 124.0 | 10292 |
| 20 | Stale cached card, relationship drift | 6/6 | 136.2 | 11853 |
| 21 | Slack channel, retired account identifier | 6/6 | 111.0 | 9537 |
| 22 | Doc section, multi-author document | 6/6 | 238.8 | 13362 |
| 23 | Two horizons disagree, card extended | 6/6 | 165.3 | 14917 |
| 24 | Empty recent window, confidence capped | 6/6 | 98.9 | 8404 |
| 25 | Channel-scoped card, different channel | 6/6 | 127.4 | 11107 |
| 26 | Vocabulary slots and evidence thresholds | 6/6 | 96.1 | 8026 |
| 27 | Ledger appended, not rewritten | 7/7 | 66.2 | 6060 |

## What changed since the previous baseline

**Eval 11: 3/4 to 4/4.** The card now names the build date on reuse
(`reused from cache, built 2026-08-02`). Step 2 had always asked for it, but
the Step 6 card template offered `reused from cache | rebuilt` with no slot for
a date, so the instruction had nowhere to land.

## Caveats

**Trial workspaces live inside the repo**, so `AGENTS.md` at the repo root
applies to every trial. Its "ask before creating new files" rule can suppress
the skill's own cache write, which this suite grades. It did not fire in this
run; it did in evals 12 and 22 on 2026-08-22. That intermittency is what makes
it worth fixing rather than tolerating -- it reads as variance, not as a
constant offset. The fix is to move trial runs outside the repo, which affects
every skill's suite.

**One run per eval.** A clean sweep is not proof of stability: eval 24's
confidence cap and eval 11's build-date line have each passed and failed across
runs on identical text. Treat 100% as "nothing is currently known to be broken",
not as a guarantee.

**Evals 11 and 21 were re-run individually** against the same skill revision as
the other 25. Eval 21 hit a transient `403 Unable to verify organization
membership` mid-run; eval 11's results were destroyed by a harness bug found
while fixing the escape guard (the guard sat after the cleanup that deletes
prior results, so a refused run still wiped them).
