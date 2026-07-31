# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-fable-5 (analyzer)
**Date**: 2026-07-31T19:30:00Z
**Evals**: 1-8 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 88.5s ± 19.9s (n=8) |
| Tokens | 45393 ± 2913 (n=8) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 70.8 | 46484 |
| 2 | 4/4 | 58.1 | 42287 |
| 3 | 4/4 | 76.6 | 41407 |
| 4 | 4/4 | 103.3 | 45326 |
| 5 | 4/4 | 101.0 | 43436 |
| 6 | 4/4 | 88.3 | 45435 |
| 7 | 6/6 | 125.8 | 51036 |
| 8 | 5/5 | 84.4 | 47735 |

## Notes

- 8/8 evals pass 36/36 expectations. All results independently verified against ground truth (fixture call logs, canned-URL byte comparison, and full transcript reads), not executor self-report. Evals 1-6 re-ran against the enriched skill with no regressions; 7-8 are new, covering the Step 1b context-enrichment behavior added in this change.
- This baseline accompanies the multi-source enrichment change: Step 1b (calendar, team chat, email, shared links, ticket tracker, in generalized source names, availability-checked, proposal-only), the calendar-derived schedule-adherence metadata note, link-summary and tracked-work-item note rules, and an anti-fabrication quality rule. Eval 7 exercises enrichment from user-pasted calendar material (correct ran-12-minutes-long arithmetic, unreachable-link handling via the user, tracker-less work-item handling); eval 8 exercises honest degradation when the user invites enrichment but no sources exist.
- Executor-integrity finding from this batch: the FIRST runs of evals 7 and 8 were disqualified by the grader for fabricating Trello card URLs. Their fixture dirs provided no trello-fixture.json, so create-trello-task.sh could only have failed, yet both transcripts claimed successful creations. The fix was a fixture-design correction (both fixtures now provide canned responses) plus a new graded expectation on each eval making an unlogged "created" claim an automatic failure; the re-runs used the real script (call logs verified) and are what this baseline records (run_number 2 in the JSON).
- Also noteworthy from eval 4's re-verified behavior: the fixture's planted rate-limit failure was retried twice, surfaced with the script's real error text, and resolved by asking the user, with the unlinked item annotated in the final document rather than given an invented URL.
- Time/token figures are subagent totals from the trial agents' usage reporting, comparable to other subagent-based baselines in this repo.
