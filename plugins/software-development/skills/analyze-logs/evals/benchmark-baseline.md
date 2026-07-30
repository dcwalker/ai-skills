# Skill Benchmark: analyze-logs

**Model**: claude-sonnet-5
**Date**: 2026-07-29T14:04:33Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 117.5s ± 41.9s |
| Tokens | 97268 ± 7312 |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 168.4 | 104793 |
| 2 | 6/6 | 182.7 | 103910 |
| 3 | 3/3 | 123.1 | 93966 |
| 4 | 4/4 | 179.2 | 112437 |
| 5 | 3/3 | 114.6 | 98215 |
| 6 | 2/2 | 71.0 | 90204 |
| 7 | 3/3 | 61.5 | 87214 |
| 8 | 3/3 | 96.7 | 91532 |
| 9 | 2/2 | 85.2 | 91617 |
| 10 | 3/3 | 142.3 | 98258 |
| 11 | 3/3 | 89.6 | 93753 |
| 12 | 3/3 | 95.6 | 101317 |

## Notes

- 12/12 evals pass 100% of their expectations in this initial baseline run (40/40 expectation-groups across all evals).
- This is a with_skill-only baseline (no without_skill comparison) since analyze-logs is a read-only analysis workflow skill.
- evals.json eval 4 describes its planted error as "FATAL-severity" in expected_output, but the fixture data actually tags it ERROR (no FATAL lines exist in that fixture). None of eval 4's four assertions require the literal word FATAL, so grading was unaffected -- flagged as a documentation inconsistency worth fixing in the eval's prose.
- eval 10's grader noted the report's claim that pool-exhaustion events recur "at roughly the same cadence" throughout the day doesn't match the fixture (all 10 events actually cluster in the first ~10 hours) -- outside any graded expectation, but a real accuracy nuance worth a closer look if this eval is extended.
- No systemic eval-design issues were flagged by any grader.
