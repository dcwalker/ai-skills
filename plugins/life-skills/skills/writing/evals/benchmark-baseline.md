# Skill Benchmark: writing

**Model**: claude-sonnet-5 (executor), claude-opus-5 (analyzer)
**Date**: 2026-08-24
**Evals**: 1-27 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectation Pass Rate | 141/142 (99.3%) |
| Evals Fully Passed | 26/27 |
| Time | 120.5s ± 53.8s |
| Output Tokens | 10161 ± 4719 |
| Errors | 0 |
| Skill invoked | 27/27 trials |

Measured after splitting reference material out of SKILL.md (807 to 706 lines).

## Per-eval results

| Eval | Scenario | Pass Rate | Time (s) | Tokens |
|------|----------|-----------|----------|--------|
| 1 | Peer email, rung-1 corpus | 6/6 | 145.9 | 12597 |
| 2 | New external recipient, rung-2 substitution | 5/5 | 146.3 | 10702 |
| 3 | No corpus anywhere | 5/5 | 29.3 | 2233 |
| 4 | Audience missing from the request | 4/4 | 5.5 | 339 |
| 5 | Two artifacts, two audiences, one run | 5/5 | 248.5 | 21670 |
| 6 | Rewrite an assistant-sounding draft | 4/4 | 162.7 | 14009 |
| 7 | Explicit skip-the-research override | 4/4 | 29.3 | 2279 |
| 8 | Journal entry, audience is self | 4/4 | 130.1 | 11333 |
| 9 | Voice held across two revisions | 5/5 | 129.7 | 10494 |
| 10 | Cache belonging to different accounts | 4/4 | 114.3 | 9509 |
| 11 | Own cache reused and confirmed | 4/4 | 69.8 | 5911 |
| 12 | Blog post from posts on disk | 5/5 | 177.5 | 14978 |
| 13 | Jira comment, display-name collision | 5/5 | 164.8 | 14699 |
| 14 | Slack corpus from an on-disk export | 6/6 | 140.0 | 12511 |
| 15 | General-profile fallback, personal audience | 6/6 | 72.4 | 5198 |
| 16 | Slack corpus through the connector | 6/6 | 176.6 | 15466 |
| 17 | Two-sample corpus, confidence calibration | 5/5 | 170.1 | 14043 |
| 18 | Register mismatch, banter corpus, serious news | 5/5 | 100.6 | 8565 |
| 19 | Revision pushing against the observed voice | 5/5 | 120.6 | 9858 |
| 20 | Stale cached card, relationship drift | 6/6 | 161.8 | 13206 |
| 21 | Slack channel, retired account identifier | 6/6 | 146.8 | 12802 |
| 22 | Doc section, multi-author document | 6/6 | 112.5 | 9314 |
| 23 | Two horizons disagree, card extended | 6/6 | 117.5 | 10772 |
| 24 | Empty recent window, confidence capped | 5/6 | 58.6 | 4777 |
| 25 | Channel-scoped card, different channel | 6/6 | 118.1 | 9700 |
| 26 | Vocabulary slots and evidence thresholds | 6/6 | 137.0 | 11283 |
| 27 | Ledger appended, not rewritten | 7/7 | 68.1 | 6095 |

## The split is behaviour-neutral

SKILL.md went from 807 to 706 lines, with conditional material moved to
`references/style-card.md` (new), `references/finding-samples.md`, and
`references/cache-files.md`. The four evals exercising relocated mechanics all
pass: 23 (two-horizon counts), 26 (vocabulary slots), 27 (ledger extension),
and 3 and 15 (the no-evidence path).

Material every run needs stayed in the body: the card template, Step 7's
assistant-tells checklist, the two evidence thresholds, and "write the card to
the cache". Moving those would relocate token cost rather than save it, and
Step 7's list is what keeps assistant voice out of drafts.

## Findings

**Eval 24 -- 5/6, and the failure is flakiness rather than a regression.** The
card reports `Confidence: high` where an empty recent window should cap it at
medium. Measured directly: the cap lands 2 of 3 times on the split version, and
2 of 3 on the version before it. This run caught the failing third. The rule is
stated twice, in Step 5 and again in Step 6, and both survived the split intact.
It is worth strengthening on its own, but it is not something the split caused.

## Caveats

**Trial workspaces live inside the repo**, so `AGENTS.md` at the repo root
applies to every trial. Its "ask before creating new files" rule can suppress
the skill's own cache write, which this suite grades. Fix is to move trial runs
outside the repo; it affects every skill's suite.

**One run per eval.** Eval 24 is the demonstrated case: a single trial cannot
tell a broken rule from one that lands two times in three.
