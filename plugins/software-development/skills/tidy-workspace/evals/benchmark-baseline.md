# Skill Benchmark: tidy-workspace

**Model**: claude-sonnet-5
**Date**: 2026-07-31T14:20:00Z
**Evals**: 1-12 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 69.1s ± 11.0s (n=6; see Notes) |
| Tokens | 45353 ± 4810 (n=6; see Notes) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 6/6 | — | — |
| 2 | 6/6 | 79.6 | 50131 |
| 3 | 4/4 | 61.9 | 48107 |
| 4 | 5/5 | 64.3 | 49880 |
| 5 | 4/4 | — | — |
| 6 | 4/4 | — | — |
| 7 | 4/4 | — | — |
| 8 | 4/4 | 53.9 | 46417 |
| 9 | 4/4 | — | — |
| 10 | 4/4 | — | — |
| 11 | 5/5 | 86.7 | 39366 |
| 12 | 4/4 | 68.1 | 38216 |

## Notes

- 10/10 evals pass 100% of their expectations in this initial baseline run. All results were independently verified against ground truth (direct git branch/worktree/status reads and gh-calls.log contents) rather than accepted from executor self-report alone.
- This is a with_skill-only baseline (no without_skill comparison) since tidy-workspace is a workflow skill, not a content generator.
- This batch exercised real git operations throughout: genuine ancestry vs. PR-state-only merge detection (eval 1), real worktree removal (eval 3) and real worktree preservation when dirty (eval 7), protected-branch exclusion logic (eval 6), the plan/approval gate itself being withheld correctly when not pre-approved (eval 4), and already-gone-on-remote handling for host auto-delete-on-merge (evals 3, 9) — not just trivial always-clean fixtures.
- Time/token usage figures are only available for evals 2, 3, 4, and 8. Figures for evals 1, 5, 6, 7, 9, and 10 were not captured because task usage metadata was not retrievable via a blocking TaskOutput poll for those trials — the same known tooling gap noted in every baseline this session. The aggregate time/token stats above are computed only over the evals with real data.
- This skill has no direct dependency on the gh-stub bugs found and fixed earlier this session, since none of its 10 evals exercise a `pulls/comments/<id>` or bare-subcommand-cross-match call pattern — confirmed via direct gh-calls.log review across all 10 trials.
- Evals 11-12 added 2026-07-31 to cover the new stash-cleanup step: 11 verifies the confident path (a stash whose fix already landed on main is classified superseded with the superseding commit cited and dropped, while a stash belonging to a live unmerged branch is kept, along with the branch itself) and 12 verifies the low-confidence path (an unexplained stash with no superseding commit, no related branch, and no tracker evidence must survive a blanket pre-approval and be presented as an explicit keep/drop/apply question, with the evidence checks documented rather than fabricated). Both pass 5/5 and 4/4; final git state (stash list, branches) independently verified for both rather than trusting executor self-report. Real time/token data was captured for both via the background Agent tool's usage reporting.
