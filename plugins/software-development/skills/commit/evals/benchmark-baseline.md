# Skill Benchmark: commit

**Model**: claude-sonnet-5
**Date**: 2026-07-29T05:22:51Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 57.5s ± 40.0s |
| Tokens | 56839 ± 21437 |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 101.2 | 91081 |
| 2 | 4/4 | 35.1 | 46039 |
| 3 | 3/3 | 148.6 | 93155 |
| 4 | 3/3 | 30.3 | 45650 |
| 5 | 3/3 | 39.1 | 44609 |
| 6 | 4/4 | 39.0 | 46332 |
| 7 | 4/4 | 38.2 | 45713 |
| 8 | 2/2 | 24.9 | 43108 |
| 9 | 4/4 | 78.9 | 49147 |
| 10 | 3/3 | 33.2 | 45361 |
| 11 | 3/3 | 25.8 | 44887 |
| 12 | 3/3 | 39.6 | 45257 |
| 13 | 4/4 | 114.2 | 98566 |

## Notes

- All 13 evals pass 100% (13/13 expectations-groups, no failures) in this initial baseline run.
- Executor wall-clock/token timing was only captured for evals 1, 3, and 13 (run within the same session as grading); for evals 2, 4-12, executor timing was lost to context compaction between the executor run and the grading pass, so time_seconds/tokens for those runs reflect grader-only cost, not full executor+grader cost. Treat time_seconds and tokens as a lower bound for those runs, not an apples-to-apples comparison against evals 1/3/13.
- This is a with_skill-only baseline (no without_skill comparison) since commit is a workflow skill, not a content-generation skill where a without-skill run would be meaningful.
- No eval-design issues were flagged by any grader across the 13 evals.
- The `tool_calls` field on every run is a stub default (always 0), not a measured value — it isn't wired up in the executor/grader pipeline yet. Do not read it as "zero tool calls occurred"; several evals (e.g. eval 9's pre-commit-hook failure/diagnose/retry sequence) clearly involved multiple tool invocations despite the field reading 0. Treat it as not-yet-tracked, the same way the timing/token gap above is called out rather than left to look like real signal.
