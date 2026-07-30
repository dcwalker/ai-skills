# Skill Benchmark: create-branch

**Model**: claude-sonnet-5
**Date**: 2026-07-29T23:17:26Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 104.0s ± 64.5s (evals 1-12; eval 13 excluded, see notes) |
| Tokens | 80803 ± 22201 (evals 1-12; eval 13 excluded, see notes) |

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
| 13 | 2/2 | 0.0 *(placeholder — see notes)* | 0 *(placeholder — see notes)* |

## Notes

- 13/13 evals pass 100% of their expectations in this initial baseline run.
- This is a with_skill-only baseline (no without_skill comparison) since create-branch is a workflow skill, not a content generator.
- Origin remotes were simulated as local bare git repos (not real network remotes) so push/fetch/pull behavior could be tested without any external dependency.
- One background executor agent (eval 1) briefly ran git commands against the real ai-skills dev repo instead of its isolated fixture, due to non-persistent shell state across its own tool calls -- it self-corrected before any push, and the eval-runner independently verified the real repo was left clean (no lost commits, no stray branches). All subsequent executor prompts in this batch were hardened with explicit git -C absolute-path instructions and a pre-flight remote-verification check to prevent recurrence.
- An automated security classifier flagged eval 7's push as a possible write to the real dcwalker/ai-skills GitHub repo; independently verified as a false positive (the real repo's ls-remote shows no such branch; the push only reached the local fixture origin).
- Evals 10-13 were executed and/or graded directly by the eval-runner in the main session rather than via separate subagents, due to a background-agent session-limit outage (reset 11:30am PT). This caveat is recorded in each of those four evals' underlying grading.json via a top-level grading_note field -- it is not surfaced as a per-eval entry in this aggregated file's runs[].notes (those come from grading.json's user_notes_summary, which grading_note is not part of). Verification method (checking real git/origin state, not self-report) was unchanged for all four; what differs is the loss of a fully independent second agent for the grading step.
- Eval 6's grader flagged that expectation 1's wording ("starts with feature/PROJ-701-") should be case-insensitive, since this fixture's own CONTRIBUTING.md mandates all-lowercase branch names.
- Eval 13 was executed AND graded directly by the eval-runner with no subagent involved at all, so it has no real wall-clock/token cost to report -- its time_seconds/tokens are 0 as a deliberate placeholder, not a measurement. It is excluded from the with_skill time_seconds/tokens aggregate stats above (but still counted in pass_rate, since that result is real) to avoid understating the true average cost. See the per-eval table for its 0/0 entry.
