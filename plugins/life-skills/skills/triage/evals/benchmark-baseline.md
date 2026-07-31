# Skill Benchmark: triage

**Model**: claude-sonnet-5 (executor) / claude-fable-5 (analyzer)
**Date**: 2026-07-31T18:40:00Z
**Evals**: 1-9 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 94.4% ± 15.7% |
| Time | 46.7s ± 14.5s (n=9) |
| Tokens | 340511 ± 110547 (n=9; total processed, see notes) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 2/4 | 44.0 | 320164 |
| 2 | 5/5 | 33.0 | 315433 |
| 3 | 4/4 | 34.4 | 314074 |
| 4 | 5/5 | 47.4 | 298754 |
| 5 | 4/4 | 28.2 | 172868 |
| 6 | 6/6 | 57.8 | 492572 |
| 7 | 5/5 | 63.0 | 429181 |
| 8 | 4/4 | 38.6 | 208150 |
| 9 | 6/6 | 74.1 | 513406 |

## Notes

- 8/9 evals pass 41/43 expectations; eval 1 fails 2 of 4. All results independently verified against ground truth (per-service call logs and direct JSON comparison of final stub state against seed fixtures), not executor self-report. Evals 1-6 are re-runs of the previously-100% batch on this branch; 7-9 are the new Jira-scoped evals via the schema-verified Atlassian stub, all passing on first run, including the cloudId-discovery flow, JQL project scoping, and eval 9's cross-service capture from a Jira issue into Trello.
- Eval 1 is the batch's one failure and the most instructive finding of the suite so far: across three runs since the sole-candidate scope-confirmation rule was added (one pass, two fails), the executor recurringly rationalizes "only one candidate exists, so scope is resolved" and fetches card-level detail before asking, despite the trial's SKILL.md containing both the explicit Step 0 sentence and the hardened Quality Rules constraint ("the first reply IS the Step 0 scope question... only the user can say scope is resolved"). It never mutates anything and asks well at field level, but the gate itself is not reliably honored. Recorded as-is rather than re-rolled to a passing run; further mitigation is a skill-design question (whether an instruction-only gate can be made reliable, or whether the eval's expectation should permit a survey-plus-confirmation reply shape).
- This baseline supersedes the 6-eval 2026-07-31T15:20Z run. The session-limit abort during the first attempt at this batch also produced two harness fixes recorded on this branch: `run-trials.sh` survives a failing trial and supports subset re-runs.
- Time and token figures are the executor subprocess's own reported values; tokens are total processed per trial (input + output + cache creation + cache read), dominated by cache reads and not comparable to subagent-token figures in other skills' baselines.
- Beyond graded expectations, the batch again showed good ask-first judgment: eval 7 surfaced two candidate due dates and the Medium-vs-High priority call as questions; eval 8 proposed a due-date buffer and a quote-gathering item without applying either; eval 9 left due dates to the user and flagged a now-stale sentence in the Jira description instead of silently rewriting it.
- Still deferred: staleness handling (Step 7) needs last-activity modeling in the Trello stub (the Jira stub now carries `updated` timestamps, which eval 8's staleness reasoning used), and large-set batch pacing (Step 0.5).
