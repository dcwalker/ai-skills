# Skill Benchmark: writing

**Model**: claude-sonnet-5 (executor), claude-opus-5 (analyzer)
**Date**: 2026-08-25
**Evals**: 1-27 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectation Pass Rate | 139/142 (97.9%) |
| Evals Fully Passed | 26/27 |
| Time | 127.1s ± 59.5s |
| Output Tokens | 10793 ± 5338 |
| Errors | 0 |
| Skill invoked | 26/27 trials |

Measured after splitting reference material out of SKILL.md (807 to 672 lines).

## Per-eval results

| Eval | Scenario | Pass Rate | Time (s) | Tokens |
|------|----------|-----------|----------|--------|
| 1 | Peer email, rung-1 corpus | 6/6 | 153.0 | 12805 |
| 2 | New external recipient, rung-2 substitution | 5/5 | 162.4 | 13726 |
| 3 | No corpus anywhere | 5/5 | 51.3 | 3879 |
| 4 | Audience missing from the request | 4/4 | 9.4 | 507 |
| 5 | Two artifacts, two audiences, one run | 5/5 | 210.8 | 18668 |
| 6 | Rewrite an assistant-sounding draft | 4/4 | 179.4 | 15398 |
| 7 | Explicit skip-the-research override | 4/4 | 19.3 | 1351 |
| 8 | Journal entry, audience is self | 4/4 | 130.2 | 11038 |
| 9 | Voice held across two revisions | 5/5 | 135.3 | 10357 |
| 10 | Cache belonging to different accounts | 4/4 | 186.8 | 14609 |
| 11 | Own cache reused and confirmed | 4/4 | 54.3 | 4566 |
| 12 | Blog post from posts on disk | 5/5 | 219.1 | 20518 |
| 13 | Jira comment, display-name collision | 5/5 | 161.5 | 12739 |
| 14 | Slack corpus from an on-disk export | 6/6 | 177.6 | 15424 |
| 15 | General-profile fallback, personal audience | 6/6 | 53.7 | 4053 |
| 16 | Slack corpus through the connector | 6/6 | 168.4 | 14525 |
| 17 | Two-sample corpus, confidence calibration | 5/5 | 224.3 | 19581 |
| 18 | Register mismatch, banter corpus, serious news | 5/5 | 111.3 | 9045 |
| 19 | Revision pushing against the observed voice | 5/5 | 108.6 | 8204 |
| 20 | Stale cached card, relationship drift | 6/6 | 125.3 | 11047 |
| 21 | Slack channel, retired account identifier | 6/6 | 154.4 | 13696 |
| 22 | Doc section, multi-author document | 3/6 | 64.2 | 5204 |
| 23 | Two horizons disagree, card extended | 6/6 | 137.3 | 12480 |
| 24 | Empty recent window, confidence capped | 6/6 | 114.9 | 9948 |
| 25 | Channel-scoped card, different channel | 6/6 | 137.9 | 11739 |
| 26 | Vocabulary slots and evidence thresholds | 6/6 | 131.5 | 11653 |
| 27 | Ledger appended, not rewritten | 7/7 | 50.9 | 4661 |

## Findings

**Eval 22 -- 3/6, the skill was not invoked.** A request naming a file path
rather than a recipient fires the skill about two thirds of the time; this run
caught the failing third, so no `git blame` ran on the three-author document.
Measured, not inferred: 2/3 on the trigger eval set. Worth addressing as a
description problem rather than a behaviour one.

## What the split cost, and what it did not

SKILL.md went 807 to 672 lines across two passes. The four evals exercising
relocated mechanics all pass: 23 (two-horizon counts, reported here as a
consolidated `Drift:` block rather than per-line, which the rule allows), 26
(vocabulary slots), 27 (ledger extension), and 17 (the polish ladder, now in
`references/style-card.md`).

**One trim was a real regression and is recorded here so it is not repeated.**
Compressing the `$HOME` location rule dropped four words -- "the one just
printed" -- and eval 8 immediately wrote its cache to the developer's real home
directory instead of the trial's. Escape rate was 0 in 54 trials before the
trim and 1 in 8 after. The words are back, with an explicit "if you are about
to type `/Users/`, stop". That paragraph is not prose padding; it is the only
thing standing between the skill and writing private observations into the
wrong home.

## Caveats

**Eval 24's recency cap** is flaky at 2 of 3. It passed here.

**Trial workspaces live inside the repo**, so `AGENTS.md` applies to every
trial and can suppress the cache write this suite grades.

**Evals 14-27 were re-run** after a session limit interrupted the first pass,
against the same skill revision as 1-13.

**One run per eval.** Evals 22 and 24 are the demonstrated cases: a single
trial cannot tell a broken rule from one that lands two times in three.
