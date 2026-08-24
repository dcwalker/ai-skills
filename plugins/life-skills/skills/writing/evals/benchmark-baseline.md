# Skill Benchmark: writing

**Model**: claude-sonnet-5 (executor), claude-opus-5 (analyzer)
**Date**: 2026-08-24
**Evals**: 1-27 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectation Pass Rate | 141/142 (99.3%) |
| Evals Fully Passed | 26/27 |
| Time | 123.6s ± 53.8s |
| Output Tokens | 10224 ± 4403 |
| Errors | 0 |
| Skill invoked | 27/27 trials |

Supersedes the 2026-08-23 baseline (138/142, 25/27), which predates the
description widening, and the 2026-08-13 baseline (106/111, evals 1-22), which
predates the cache-retention redesign.

## Per-eval results

| Eval | Scenario | Pass Rate | Time (s) | Tokens |
|------|----------|-----------|----------|--------|
| 1 | Peer email, rung-1 corpus | 6/6 | 150.8 | 11931 |
| 2 | New external recipient, rung-2 substitution | 5/5 | 194.8 | 16520 |
| 3 | No corpus anywhere | 5/5 | 37.3 | 2864 |
| 4 | Audience missing from the request | 4/4 | 10.5 | 731 |
| 5 | Two artifacts, two audiences, one run | 5/5 | 187.1 | 17123 |
| 6 | Rewrite an assistant-sounding draft | 4/4 | 136.5 | 11164 |
| 7 | Explicit skip-the-research override | 4/4 | 16.2 | 1063 |
| 8 | Journal entry, audience is self | 4/4 | 134.3 | 11432 |
| 9 | Voice held across two revisions | 5/5 | 110.8 | 8624 |
| 10 | Cache belonging to different accounts | 4/4 | 166.8 | 15255 |
| 11 | Own cache reused and confirmed | 3/4 | 94.6 | 8284 |
| 12 | Blog post from posts on disk | 5/5 | 179.8 | 15552 |
| 13 | Jira comment, display-name collision | 5/5 | 141.7 | 12349 |
| 14 | Slack corpus from an on-disk export | 6/6 | 121.7 | 10703 |
| 15 | General-profile fallback, personal audience | 6/6 | 62.2 | 4857 |
| 16 | Slack corpus through the connector | 6/6 | 151.0 | 12995 |
| 17 | Two-sample corpus, confidence calibration | 5/5 | 183.6 | 15474 |
| 18 | Register mismatch, banter corpus, serious news | 5/5 | 91.1 | 7528 |
| 19 | Revision pushing against the observed voice | 5/5 | 89.0 | 6914 |
| 20 | Stale cached card, relationship drift | 6/6 | 171.6 | 14551 |
| 21 | Slack channel, retired account identifier | 6/6 | 127.1 | 10678 |
| 22 | Doc section, multi-author document | 6/6 | 232.5 | 11878 |
| 23 | Two horizons disagree, card extended | 6/6 | 134.9 | 11786 |
| 24 | Empty recent window, confidence capped | 6/6 | 106.3 | 8574 |
| 25 | Channel-scoped card, different channel | 6/6 | 96.9 | 8632 |
| 26 | Vocabulary slots and evidence thresholds | 6/6 | 123.5 | 10913 |
| 27 | Ledger appended, not rewritten | 7/7 | 85.5 | 7680 |

## What changed since the previous baseline

**Eval 22: 3/6 to 6/6.** It previously never invoked the skill -- a request
naming a file path read as a file-edit task -- so no `git blame` ran on a
three-author document. After the description named repository prose explicitly,
the trial invoked the skill, ran blame, and separated the user's two sections
from Priya's and Jordan's. Trigger rate on doc-section prompts, measured over
three runs, went from 1/3 to 2/3.

**Eval 24: 5/6 to 6/6.** The recency cap applied: `medium (capped from high --
no samples in the last 12 months)`. This has passed and failed across runs on
identical text, so treat it as variance that landed well rather than as fixed.

**Skill invoked in 27/27 trials**, up from 26/27.

## Findings

**Eval 11 -- 3/4, build date not named.** The card is reported as reused and
its age is available (sample range plus `Confirmed: 2026-08-24`), but the
2026-08-02 build date is not named, which the expectation asks for. Worth
noting the expectation predates this redesign: cards no longer carry a `Built:`
line at all, having replaced it with `Ledger:` and `Confirmed:`. The eval
likely needs updating to the current format rather than the skill needing a
fix, but it is recorded as a failure rather than quietly amended.

## Caveats

**Trial workspaces live inside the repo**, so `AGENTS.md` at the repo root
applies to every trial. Its "ask before creating new files" rule can suppress
the skill's own cache write -- observed in evals 12 and 22 on 2026-08-22,
absent in this run -- which makes it an intermittent understatement of real
behaviour rather than a constant offset. The fix is to move trial runs outside
the repo; it affects every skill's suite and was deliberately deferred.

**One run per eval.** Eval 11's build-date line and eval 24's confidence cap
have each passed and failed across runs on identical text.
