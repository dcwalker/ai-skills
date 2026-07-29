# Skill Benchmark: conduct-interview

**Model**: claude-sonnet-5
**Date**: 2026-07-29T13:50:37Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 97% ± 9% |
| Time | 146.3s ± 22.8s |
| Tokens | 95368 ± 1912 |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 3/4 | 183.1 | 96785 |
| 2 | 3/3 | 168.3 | 97507 |
| 3 | 3/3 | 121.4 | 96748 |
| 4 | 3/3 | 142.8 | 92715 |
| 5 | 3/3 | 161.6 | 95155 |
| 6 | 3/3 | 135.3 | 92374 |
| 7 | 3/3 | 138.7 | 95278 |
| 8 | 3/3 | 119.0 | 96385 |

## Notes

- 12 of 13 expectation-groups pass across 8 evals (eval 1 has 1 genuine failure: two Step 2 interview turns bundled multiple distinct questions into one turn, violating the skill's one-question-at-a-time rule -- confirmed directly against the transcript, not just the self-report).
- This is a with_skill-only baseline (no without_skill comparison) since conduct-interview is a workflow skill, not a content-generation skill.
- All evals are pure conversational simulations (no git fixtures or gh-stub) -- the executor plays both the skill and the simulated user in a single agent turn, then a separate grader agent independently re-reads the resulting transcript.
- No systemic eval-design issues were flagged by any grader.
