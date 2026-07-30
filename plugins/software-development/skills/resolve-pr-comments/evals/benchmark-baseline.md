# Skill Benchmark: resolve-pr-comments

**Model**: claude-sonnet-5
**Date**: 2026-07-30T22:30:00Z
**Evals**: 1-12 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 61.2s ± 12.7s (n=6; see Notes) |
| Tokens | 48406 ± 1889 (n=6; see Notes) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | — | — |
| 2 | 4/4 | 63.4 | 49503 |
| 3 | 4/4 | 65.3 | 49092 |
| 4 | 5/5 | — | — |
| 5 | 5/5 | — | — |
| 6 | 5/5 | — | — |
| 7 | 3/3 | 42.1 | 45551 |
| 8 | 4/4 | 64.5 | 48935 |
| 9 | 4/4 | — | — |
| 10 | 4/4 | 79.6 | 50627 |
| 11 | 5/5 | — | — |
| 12 | 3/3 | 52.3 | 46729 |

## Notes

- 12/12 evals pass 100% of their expectations in this initial baseline run. All results were independently verified against ground truth (direct file reads, git log/show, and gh-calls.log contents) rather than accepted from executor self-report alone.
- This is a with_skill-only baseline (no without_skill comparison) since resolve-pr-comments is a workflow skill, not a content generator.
- Time/token usage figures are only available for evals 2, 3, 7, 8, 10, and 12. Figures for evals 1, 4, 5, 6, 9, and 11 were not captured because task usage metadata was not retrievable via a blocking TaskOutput poll for those trials — the same known tooling gap noted in prior baselines this session. The aggregate time/token stats above are computed only over the 6 evals with real data.
- A serious real gh-stub bug was found and fixed during this baseline run (extending [#16](https://github.com/dcwalker/ai-skills/pull/16)): `_bounded_contains` required a non-alphanumeric character on BOTH sides of a match, unconditionally — but a path-fragment match entry like `["pulls/comments/"]` deliberately ends in a delimiter, and the character that follows it in a real call is always a numeric comment ID (alphanumeric), so the entry could never match for any comment ID. This blocked the reply/resolve step of every eval in this skill's first pass (evals 1-4 all hit it independently; two executors correctly diagnosed the identical root cause and stopped rather than patching shared infrastructure themselves). Fixed by only enforcing a boundary check on a side where the match substring's own edge character is alphanumeric. Verified with unit tests and a full replay of 241 previously-recorded gh-calls.log entries across every baselined skill: 231 resolve identically, and the remaining 10 are this bug plus the earlier bare-subcommand fix being corrected (including 6 resolve-pr-comments calls that previously had no match at all).
- Evals 1-4 were run twice: the first pass hit the gh-stub bug above and stopped cleanly (no fabricated success), and the second pass (reported here) ran cleanly against the fixed stub. This is noted for transparency, not as a finding about the resolve-pr-comments skill itself, which behaved correctly in both passes up to the point of the infrastructure blocker.
- This batch covered a strong mix of scenarios: valid single-file fixes (1, 8-decline, 10-security), a genuine non-code clarifying question (2), an already-fixed-by-later-commit case (3), bot/human filtering in both directions (4, 5), independent multi-comment handling with one valid + one invalid (6), zero-comments (7), a cross-file single-issue fix (9), fully independent multi-comment handling with two valid issues (11), and an already-resolved-thread no-op (12).
