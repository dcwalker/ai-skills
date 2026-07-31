# Skill Benchmark: conduct-interview

**Model**: claude-sonnet-5
**Date**: 2026-07-31T15:45:00Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 136.5s ± 20.1s |
| Tokens | 87428 ± 20543 |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 4/4 | 104.6 | 33263 |
| 2 | 3/3 | 168.3 | 97507 |
| 3 | 3/3 | 121.4 | 96748 |
| 4 | 3/3 | 142.8 | 92715 |
| 5 | 3/3 | 161.6 | 95155 |
| 6 | 3/3 | 135.3 | 92374 |
| 7 | 3/3 | 138.7 | 95278 |
| 8 | 3/3 | 119.0 | 96385 |

## Notes

- In the ORIGINAL 2026-07-29 baseline run, 12 of 13 expectation-groups passed across 8 evals; eval 1's one genuine failure (two Step 2 interview turns bundling multiple distinct questions into one turn) was later fixed and re-run at 4/4 (see the final note), which is what the tables above reflect.
- This is a with_skill-only baseline (no without_skill comparison) since conduct-interview is a workflow skill, not a content-generation skill.
- All evals are pure conversational simulations (no git fixtures or gh-stub) -- the executor plays both the skill and the simulated user in a single agent turn, then a separate grader agent independently re-reads the resulting transcript.
- No systemic eval-design issues were flagged by any grader.
- 2026-07-31: after the original baseline's eval 1 finding, the one-question rule was redefined around the line of inquiry: a clarifying follow-up that narrows the same inquiry may share a turn, while asks about different subjects may not, regardless of punctuation. Eval 1's first expectation was updated to grade that distinction and the eval re-run against the amended skill: 4/4, with single-inquiry turns throughout, a separate-turn clarifying follow-up on a vague answer, and a [confirm ...] marker resolved only when the user supplied the fact. The per-eval row above reflects the re-run (run_number 2 in the JSON); the token drop for eval 1 also reflects the re-run using a different measurement context than the original batch.
