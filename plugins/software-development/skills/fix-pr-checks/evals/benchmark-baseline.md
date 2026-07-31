# Skill Benchmark: fix-pr-checks

**Model**: claude-sonnet-5
**Date**: 2026-07-31T14:45:00Z
**Evals**: 1-10 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 85.8s ± 24.8s (n=10) |
| Tokens | 45762 ± 2868 (n=10) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 81.2 | 47474 |
| 2 | 4/4 | 99.4 | 39925 |
| 3 | 4/4 | 103.2 | 47711 |
| 4 | 5/5 | 101.2 | 49645 |
| 5 | 4/4 | 45.3 | 45077 |
| 6 | 3/3 | 90.6 | 47392 |
| 7 | 4/4 | 95.0 | 48522 |
| 8 | 4/4 | 60.6 | 44680 |
| 9 | 4/4 | 52.2 | 45190 |
| 10 | 4/4 | 129.4 | 42002 |

## Notes

- 10/10 evals were run and independently verified against ground truth (direct file reads, `git log`/`show`, and actually executing the fixture's `check.py`/`check2.py` scripts) rather than accepted from executor self-report alone. In the ORIGINAL 2026-07-31T02:30Z baseline run, 8/10 evals passed 100% of their expectations while evals 2 and 10 each passed only a fraction due to the behavior gap described below; both were later re-run against the amended skill and now pass 4/4 (see the final note), which is what the per-eval table above reflects.
- This is a with_skill-only baseline (no without_skill comparison) since fix-pr-checks is a workflow skill, not a content generator.
- **A genuine, non-deterministic behavior gap was found and is the main finding of this baseline**: for a subset of evals (2 and 10), the executor correctly diagnosed the failing check's real root cause but then stopped and asked for permission before actually applying the fix, instead of autonomously fixing, verifying, committing, and pushing as `fix-pr-checks`' own SKILL.md instructs. This happened despite the user prompts for these two evals being plain, low-risk, directly-requested bug fixes with no ambiguity or risk signal that would normally warrant a pause — and despite four other evals in this same batch (1, 4, 6, 7) with equivalent-shaped prompts proceeding straight to fix-and-commit without pausing. One of the pausing-vs-proceeding trials (eval 6, which did proceed) explicitly reasoned in its own transcript about the tension between the user's real global "ask before code changes" rule and the direct nature of the request, and judged the request itself as sufficient authorization — suggesting the inconsistency across evals 2/10 vs. 1/4/6/7 comes from that same rule being applied non-deterministically by the executor, not from a deterministic property of the fix-pr-checks skill's own instructions (which are unambiguous: fix, verify, commit, push, no gating).
- Every diagnosis in this batch — including evals 2 and 10 — was factually correct even when the executor stopped short of applying it. No fabricated successes, no incorrect root-cause attribution, and no speculative fixes were observed anywhere in the batch.
- This batch covered a strong mix of scenarios: a straightforward single-file fix (1), a fix requiring tracing through an indirect call path rather than trusting the check output's surface-level file reference (2), an unfixable infrastructure failure with no local code cause (3), two independent unrelated bugs in one PR (4), an all-green status check (5), a mix of one real bug, one already-passing check, and one in-progress check that must not be treated as failing (6), a CodeQL security annotation requiring a targeted fix (7), a PR with zero checks run yet (8), a vague, non-locally-reproducible infrastructure failure requiring the skill to stop and ask rather than loop (9), and a regression-detection scenario where fixing the named check surfaces a second, newly-failing check that must also be caught (10).
- The `tool_calls` and `errors` fields on every run are `null`, not measured — they aren't wired up in the executor/grader pipeline yet.
- 2026-07-31: after the ask-vs-proceed non-determinism finding (see the earlier note), a new "Authorization context" section was added to SKILL.md making an explicit fix-the-checks request constitute the approval for the code changes those fixes require, satisfying any ambient ask-before-changing rule, while keeping diagnostic-only requests read-only and preserving the pause for fixes that raise genuinely new decisions. Evals 2 and 10 (the two that previously paused to ask) were re-run against the updated skill: both now proceed straight to fix-verify-commit and pass 4/4, independently verified against final file contents, commit history, and the fixture checks executing cleanly. The per-eval rows above reflect the re-runs (run_number 2 in the JSON); the aggregate summary reflects them.
