# Skill Benchmark: review-readme

**Model**: claude-sonnet-5
**Date**: 2026-07-30T22:45:00Z
**Evals**: 1-13 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 78.3s ± 18.7s (n=6; see Notes) |
| Tokens | 51510 ± 2107 (n=6; see Notes) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 3/3 | — | — |
| 2 | 3/3 | 93.4 | 53378 |
| 3 | 3/3 | 63.1 | 49232 |
| 4 | 4/4 | — | — |
| 5 | 3/3 | — | — |
| 6 | 3/3 | — | — |
| 7 | 2/2 | 75.7 | 52047 |
| 8 | 3/3 | 54.8 | 48806 |
| 9 | 2/2 | — | — |
| 10 | 2/2 | — | — |
| 11 | 3/3 | — | — |
| 12 | 3/3 | 77.6 | 51657 |
| 13 | 3/3 | 105.3 | 53940 |

## Notes

- 13/13 evals pass 100% of their expectations in this initial baseline run. All results were independently verified against ground truth (direct file reads, grep against the final README, and cross-checks against package.json/CONTRIBUTING.md/the actual repo file layout) rather than accepted from executor self-report alone.
- This is a with_skill-only baseline (no without_skill comparison) since review-readme is a workflow skill, not a content generator.
- This skill has no gh/GitHub interaction at all — fixtures are plain local file trees with no gh-stub cassette involved, so this batch was unaffected by the gh-stub bugs found and fixed while baselining other skills this session.
- Time/token usage figures are only available for evals 2, 3, 7, 8, 12, and 13. Figures for evals 1, 4, 5, 6, 9, 10, and 11 were not captured because task usage metadata was not retrievable via a blocking TaskOutput poll for those trials — the same known tooling gap noted in prior baselines this session. The aggregate time/token stats above are computed only over the 6 evals with real data.
- Eval 4 (the clean-fixture guard case) is a strong positive result: the executor independently re-verified every command, port number, and Node version against the actual codebase before concluding no changes were needed, rather than assuming the prompt's framing. It made zero edits, and the final README is byte-for-byte identical to the fixture's original — avoiding the "invents busywork to seem useful" failure mode this eval specifically guards against.
- This batch covered a strong mix of real documentation defects: stale commands (1, 9, 12), duplicate content (2), a genuinely unresolvable broken link handled by removal rather than fabrication (3), a clean-fixture guard (4), documentation gaps (5, 8), a broken/incomplete table of contents (6), a heading hierarchy violation (7), inconsistent code-fence formatting (10), a wall-of-text paragraph needing restructuring without information loss (11), a CONTRIBUTING.md guideline overriding the skill's npm default (12), and an outdated directory tree (13).
- The `tool_calls` and `errors` fields on every run in the JSON are `null`, not measured — they aren't wired up in the executor/grader pipeline yet.
