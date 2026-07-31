# Skill Benchmark: review-code

**Model**: claude-sonnet-5
**Date**: 2026-07-31T14:30:00Z
**Evals**: 1-14 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 102.1s ± 26.5s (n=14) |
| Tokens | 48108 ± 4063 (n=14) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 99.9 | 48679 |
| 2 | 3/3 | 97.8 | 47214 |
| 3 | 4/4 | 121.7 | 52014 |
| 4 | 3/3 | 73.8 | 47859 |
| 5 | 3/3 | 83.5 | 49510 |
| 6 | 3/3 | 133.8 | 49743 |
| 7 | 3/3 | 163.7 | 53836 |
| 8 | 4/4 | 117.7 | 51445 |
| 9 | 4/4 | 87.9 | 48299 |
| 10 | 3/3 | 76.3 | 48021 |
| 11 | 3/3 | 109.7 | 49749 |
| 12 | 4/4 | 96.8 | 48548 |
| 13 | 5/5 | 111.1 | 41278 |
| 14 | 4/4 | 55.0 | 37313 |

## Notes

- 12/12 evals pass 100% of their expectations in this baseline run. All results were independently verified against ground truth: every eval's target repository was confirmed untouched (`git status` clean, since review-code should never modify files), and every review finding was checked against the actual fixture source files rather than accepted from executor self-report alone.
- This is a with_skill-only baseline (no without_skill comparison) since review-code is a workflow/analysis skill, not a content generator.
- Eval 2's original `expected_output`/expectations assumed its fixture function (`applyDiscount`) had "no real defects" and mandated a None/Low (0-39) risk score. A direct read of the fixture code shows this assumption was inaccurate: the function genuinely has no bounds check on its percentage argument (can silently produce a negative price) and no NaN guard. Corrected the expectation to grade against the code's real state (a genuine, minor-to-moderate defensive-coding gap, not a security or correctness emergency) rather than an idealized "this code is perfect" assumption — consistent with the same class of fixture-narrative corrections made elsewhere in this session's baselines.
- This batch covered a strong mix of scenarios: a broken-object-level-authorization plus missing-validation case (1), a repo with no guideline files at all requiring a fallback to general best practices (2), an unambiguous SQL injection (3), a fully clean fixture that must score near-zero without invented findings (4), a decoy case where surface-level patterns (`any` types, TODO comments) are explicitly permitted by the repo's own guidelines and must not be flagged (5), missing async error handling (6), a rate-limiter with a real, empirically-verified prototype-pollution bypass plus a lifetime-cap design flaw (7), unmasked sensitive data logging governed by an AGENTS.md-specific rule (8), a missing-timeout rule governed by a CLAUDE.md-specific rule (9), a null-dereference crash documented by the callee's own code comments (10), a side-by-side compliant-vs-violating endpoint pair that must be distinguished rather than treated identically (11), and a missing-test-coverage finding that must correctly distinguish an already-covered endpoint from an uncovered new one (12).
- The `tool_calls` and `errors` fields on every run are `null`, not measured — they aren't wired up in the executor/grader pipeline yet.
- Evals 13-14 added 2026-07-31 to cover the new Step 4b (Skill Quality Review) behavior: 13 verifies the additive skill-quality path on a diff touching a skill file (section present, static checks reported, evals NOT run by default with the checked-in baseline cited as the result of record) and 14 verifies the negative case (a non-skill diff in a repo that contains a skill directory must not trigger the section, while the general review still catches a planted SQL-injection violation). Both pass 5/5 and 4/4 respectively; both independently verified against the trial transcripts and post-trial workspace state (no files modified, no eval subagents spawned) rather than executor self-report. Eval 13's executor also correctly flagged the fixture's deliberately stale baseline as a Medium finding — consistent with CONTRIBUTING.md's Evals policy — which the eval's expectations do not require but do not forbid.
