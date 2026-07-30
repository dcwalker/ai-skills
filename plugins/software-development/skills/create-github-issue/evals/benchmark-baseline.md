# Skill Benchmark: create-github-issue

**Model**: claude-sonnet-5
**Date**: 2026-07-30T14:16:21Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 143.8s ± 44.3s |
| Tokens | 101727 ± 15931 |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 213.5 | 105905 |
| 2 | 4/4 | 109.3 | 90568 |
| 3 | 3/3 | 87.6 | 90953 |
| 4 | 4/4 | 117.7 | 94803 |
| 5 | 3/3 | 171.3 | 98020 |
| 6 | 4/4 | 80.0 | 89168 |
| 7 | 4/4 | 162.2 | 99980 |
| 8 | 3/3 | 193.1 | 104603 |
| 9 | 4/4 | 155.5 | 144027 |
| 10 | 5/5 | 147.8 | 99247 |

## Notes

- 10/10 evals pass 100% of their expectations in this initial baseline run.
- This is a with_skill-only baseline (no without_skill comparison) since create-github-issue is a workflow skill, not a content generator.
- The gh-stub's substring-based cassette matching produced false-positive matches in most evals in this batch: a --json field list or issue title containing a substring like "label", "milestone", or "list" sometimes collided with an unrelated cassette entry (e.g. matching the label-list fixture instead of the intended issue-list call). Executors detected and worked around this every time by rewording the call, so it never affected a graded outcome, but it is a real gh-stub harness bug worth fixing (e.g. exact-argv or token-boundary matching) since it added noticeable, unnecessary recovery work to nearly every trial.
- The gh-stub only logs argv, not the contents of files referenced by flags like --body-file. Expectations that check drafted issue-body content had to rely on the transcript's self-report for that portion rather than independently-verifiable ground truth. Consider having the stub optionally capture referenced file contents if exact body verification becomes important.
- Eval 9 ran across two agent turns in this session (the first turn stopped right after presenting the combined optional-field confirmation; it was resumed via a follow-up message to complete the approval-and-create sequence) -- the final outcome and grading were unaffected, but its executor token/time figures sum both turns.
