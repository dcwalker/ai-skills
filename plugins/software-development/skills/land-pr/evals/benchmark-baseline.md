# Skill Benchmark: land-pr

**Model**: claude-sonnet-5
**Date**: 2026-07-30T21:40:00Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8, 9 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 90.3s ± 85.9s (n=3; see Notes) |
| Tokens | 51275 ± 10587 (n=3; see Notes) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | — | — |
| 2 | 6/6 | — | — |
| 3 | 5/5 | — | — |
| 4 | 5/5 | — | — |
| 5 | 4/4 | 38.6 | 45088 |
| 6 | 4/4 | 42.9 | 45237 |
| 7 | 4/4 | — | — |
| 8 | 5/5 | — | — |
| 9 | 4/4 | 189.4 | 63500 |

## Notes

- 9/9 evals pass 100% of their expectations in this initial baseline run. All results were independently verified against ground truth (git log/branch state, gh-calls.log contents, config.py contents, grep for conflict markers) rather than accepted from executor self-report alone.
- This is a with_skill-only baseline (no without_skill comparison) since land-pr is an orchestration/workflow skill, not a content generator.
- This batch exercised real git conflict resolution (evals 2 and 8 — genuine merge conflicts in config.py's VERSION line, resolved for real via fetch/merge/resolve/commit/push, not simulated) and real CI-failure remediation (evals 4, 7, and 8 — actual bugs/missing files in the fixture repos, fixed and verified locally before push), exercising the skill's core orchestration logic (round looping, sub-skill invocation, round-cap handling) against realistic scenarios rather than trivial always-green fixtures.
- Time/token usage figures are only available for evals 5, 6, and 9. Figures for evals 1, 2, 3, 4, 7, and 8 were not captured because task usage metadata was not retrievable via a blocking TaskOutput poll for those trials (only background task-notification completions surfaced a usage tag in this session). The aggregate time/token stats above are computed only over the 3 evals with real data and should not be read as representative of the other 6 — a known tooling gap, consistent with the same gap noted in the implement-feature baseline.
- Eval 9 independently confirmed the gh-stub word-boundary matching bug fixed in PR #11 (not yet merged to `main` at the time of this run) is real and still live on `main`: its trial hit the exact false-positive (`["pr","merge"]` guard matching inside "mergeable"/"mergeStateStatus") and the executor correctly diagnosed and worked around it without modifying the shared repo. Subsequent trials in this batch were run from the branch containing the fix to avoid repeating this.
