# Skill Benchmark: create-branch

**Model**: claude-sonnet-5
**Date**: 2026-07-29T23:17:26Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 96.0s ± 68.2s |
| Tokens | 74587 ± 30888 |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 275.1 | 106598 |
| 2 | 4/4 | 128.4 | 93828 |
| 3 | 3/3 | 145.8 | 97215 |
| 4 | 2/2 | 52.0 | 85869 |
| 5 | 3/3 | 105.1 | 91922 |
| 6 | 3/3 | 111.0 | 90091 |
| 7 | 3/3 | 125.8 | 91731 |
| 8 | 3/3 | 59.2 | 87542 |
| 9 | 3/3 | 94.2 | 89705 |
| 10 | 3/3 | 57.3 | 45880 |
| 11 | 3/3 | 36.5 | 43995 |
| 12 | 3/3 | 58.1 | 45258 |
| 13 | 2/2 | 0.0 | 0 |

## Notes

- 13/13 evals pass 100% of their expectations in this initial baseline run.
- This is a with_skill-only baseline (no without_skill comparison) since create-branch is a workflow skill, not a content generator.
- Origin remotes were simulated as local bare git repos (not real network remotes) so push/fetch/pull behavior could be tested without any external dependency.
- One background executor agent (eval 1) briefly ran git commands against the real ai-skills dev repo instead of its isolated fixture, due to non-persistent shell state across its own tool calls -- it self-corrected before any push, and the eval-runner independently verified the real repo was left clean (no lost commits, no stray branches). All subsequent executor prompts in this batch were hardened with explicit git -C absolute-path instructions and a pre-flight remote-verification check to prevent recurrence.
- An automated security classifier flagged eval 7's push as a possible write to the real dcwalker/ai-skills GitHub repo; independently verified as a false positive (the real repo's ls-remote shows no such branch; the push only reached the local fixture origin).
- Evals 10-13 were executed and/or graded directly by the eval-runner in the main session rather than via separate subagents, due to a background-agent session-limit outage (reset 11:30am PT) -- flagged per-eval via a grading_note field. Verification method (checking real git/origin state, not self-report) was unchanged; what differs is the loss of a fully independent second agent for the grading step on these four evals.
- Eval 6's grader flagged that expectation 1's wording ("starts with feature/PROJ-701-") should be case-insensitive, since this fixture's own CONTRIBUTING.md mandates all-lowercase branch names.
