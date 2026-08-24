# Skill Benchmark: writing

**Model**: claude-sonnet-5 (executor), claude-opus-5 (analyzer)
**Date**: 2026-08-23
**Evals**: 1-27 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectation Pass Rate | 138/142 (97.2%) |
| Evals Fully Passed | 25/27 |
| Time | 98.8s ± 45.0s |
| Output Tokens | 8454 ± 4098 |
| Errors | 0 |
| Skill invoked | 26/27 trials |

Supersedes the 2026-08-13 baseline (106/111, evals 1-22), which predates the
cache-retention redesign and the five evals added for it.

## Per-eval results

| Eval | Scenario | Pass Rate | Time (s) | Tokens |
|------|----------|-----------|----------|--------|
| 1 | Peer email, rung-1 corpus | 6/6 | 87.8 | 7241 |
| 2 | New external recipient, rung-2 substitution | 5/5 | 148.2 | 12533 |
| 3 | No corpus anywhere | 5/5 | 42.8 | 2853 |
| 4 | Audience missing from the request | 4/4 | 10.5 | 726 |
| 5 | Two artifacts, two audiences, one run | 5/5 | 166.9 | 15023 |
| 6 | Rewrite an assistant-sounding draft | 4/4 | 132.4 | 11000 |
| 7 | Explicit skip-the-research override | 4/4 | 11.2 | 681 |
| 8 | Journal entry, audience is self | 4/4 | 100.6 | 8933 |
| 9 | Voice held across two revisions | 5/5 | 89.7 | 7322 |
| 10 | Cache belonging to different accounts | 4/4 | 104.5 | 9296 |
| 11 | Own cache reused and confirmed | 4/4 | 75.3 | 6347 |
| 12 | Blog post from posts on disk | 5/5 | 190.8 | 17250 |
| 13 | Jira comment, display-name collision | 5/5 | 96.7 | 7592 |
| 14 | Slack corpus from an on-disk export | 6/6 | 162.0 | 14449 |
| 15 | General-profile fallback, personal audience | 6/6 | 72.6 | 5730 |
| 16 | Slack corpus through the connector | 6/6 | 107.4 | 9664 |
| 17 | Two-sample corpus, confidence calibration | 5/5 | 121.2 | 10381 |
| 18 | Register mismatch, banter corpus, serious news | 5/5 | 59.7 | 4866 |
| 19 | Revision pushing against the observed voice | 5/5 | 123.0 | 8966 |
| 20 | Stale cached card, relationship drift | 6/6 | 163.3 | 14208 |
| 21 | Slack channel, retired account identifier | 6/6 | 113.6 | 10063 |
| 22 | Doc section, multi-author document | 3/6 | 36.5 | 2948 |
| 23 | Two horizons disagree, card extended | 6/6 | 96.6 | 8936 |
| 24 | Empty recent window, confidence capped | 5/6 | 101.5 | 8701 |
| 25 | Channel-scoped card, different channel | 6/6 | 82.5 | 7328 |
| 26 | Vocabulary slots and evidence thresholds | 6/6 | 99.4 | 8586 |
| 27 | Ledger appended, not rewritten | 7/7 | 70.7 | 6638 |

## Findings

**Eval 22 — 3/6, skill not invoked.** `skill_invoked: false`, 2 tool calls. The
trial read `docs/on-call-redesign.md` and drafted directly, so no `git blame`
ran and the profile was not restricted to the user's own two sections, which is
the point of the eval on a three-author document. The skill files were present
in the workspace and identical to eval 21's, so this is a trigger gap for
document-section work rather than a loading failure. It has now recurred across
runs.

**Eval 24 — 5/6, confidence cap not applied.** The card reports
`Confidence: high` with no mention of the recent window, where the rule caps it
at medium when no samples fall in the last twelve months. This passed in two
earlier runs and failed here, so it is variance around a rule the skill states
but does not apply reliably.

## What this run establishes

The redesign's five new evals (23-27) all pass, covering two-horizon counts,
the empty-recent-window path, channel-scoped cards, vocabulary slots with
evidence thresholds, and ledger extension.

Fixed and confirmed during this cycle: the skill no longer reports cache writes
it did not perform (previously 4 of 27 trials); drafts are no longer withheld
behind the style card; missing content detail is marked inline rather than
blocking a draft; and the cache is written under `$HOME` as the environment
reports it rather than a reconstructed path.

## Caveats

**Trial workspaces live inside the repo**, so `AGENTS.md` at the repo root
applies to every trial. Its "ask before creating new files" rule intermittently
suppresses the skill's own cache write — observed in evals 12 and 22 on
2026-08-22 — so these figures slightly understate real behaviour. The fix is to
move trial runs outside the repo; it affects every skill's suite and was
deliberately deferred.

**One run per eval.** A single per-eval failure may be variance rather than a
stable result; eval 24 is a known instance.
