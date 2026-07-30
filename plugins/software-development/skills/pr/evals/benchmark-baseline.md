# Skill Benchmark: pr

**Model**: claude-sonnet-5
**Date**: 2026-07-30T22:10:00Z
**Evals**: 1-14 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 55.1s ± 15.5s (n=7; see Notes) |
| Tokens | 46550 ± 1860 (n=7; see Notes) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 6/6 | — | — |
| 2 | 3/3 | — | — |
| 3 | 3/3 | 52.5 | 46192 |
| 4 | 3/3 | — | — |
| 5 | 3/3 | — | — |
| 6 | 2/2 | 64.5 | 48127 |
| 7 | 2/2 | 65.3 | 46019 |
| 8 | 3/3 | 37.7 | 45332 |
| 9 | 3/3 | — | — |
| 10 | 3/3 | — | — |
| 11 | 3/3 | 79.6 | 50008 |
| 12 | 3/3 | — | — |
| 13 | 3/3 | 47.7 | 44834 |
| 14 | 2/2 | 38.3 | 45339 |

## Notes

- 14/14 evals pass 100% of their expectations in this initial baseline run. All results were independently verified against ground truth (direct reads of each trial's gh-calls.log) rather than accepted from executor self-report alone.
- This is a with_skill-only baseline (no without_skill comparison) since pr is a workflow skill, not a content generator.
- Time/token usage figures are only available for evals 3, 6, 7, 8, 11, 13, and 14. Figures for evals 1, 2, 4, 5, 9, 10, and 12 were not captured because task usage metadata was not retrievable via a blocking TaskOutput poll for those trials — the same known tooling gap noted in the implement-feature and land-pr baselines. The aggregate time/token stats above are computed only over the 7 evals with real data.
- A real gh-stub cassette-matching bug was found and fixed during this baseline run ([#16](https://github.com/dcwalker/ai-skills/pull/16)): a multi-element cassette entry made entirely of bare subcommand words (e.g. `["pr", "list"]`) could match inside a completely different call's `--body`/`--title` free-text VALUE if that text happened to contain the same word as a bounded token (e.g. a PR description mentioning "...the items list..." false-matching a `["pr", "list"]` guard). Surfaced in eval 10 (a `pr edit --body ...` call whose logged argv was correct but whose stub-returned stdout was the wrong fixture); replaying all 213 previously-recorded gh-calls.log entries from every baselined skill confirmed only 4 calls were affected by this bug (evals 4, 5, and 10 in this batch, plus a previously-unnoticed instance in create-github-issue eval 8), all now resolved correctly. Since grading is based on logged argv (ground truth), not stub stdout, none of this affected any eval's pass/fail outcome — it only affected what canned response the executor saw mid-trial.
- Two trials (evals 4 and 5) show an extra, executor-initiated diagnostic `gh pr create` call in their logs beyond the real PR-creation call, made while the executor was investigating unrelated stub behavior. This is executor noise, not skill behavior, and doesn't affect any expectation.
- Eval 9's executor reported that its first `gh pr view` attempt ran without the gh-stub on PATH (a shell-state reset between Bash tool calls in the executor's own environment) and hit a real network error before self-correcting. The call was read-only and failed, so no mutation occurred and no real repository was affected.
