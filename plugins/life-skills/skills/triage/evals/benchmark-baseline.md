# Skill Benchmark: triage

**Model**: claude-sonnet-5 (executor) / claude-fable-5 (analyzer)
**Date**: 2026-07-31T15:20:00Z
**Evals**: 1-6 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 40.5s ± 9.2s (n=6) |
| Tokens | 288202 ± 102970 (n=6; total processed, see notes) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 4/4 | 27.4 | 182772 |
| 2 | 5/5 | 42.9 | 259838 |
| 3 | 4/4 | 36.4 | 447464 |
| 4 | 5/5 | 52.2 | 267428 |
| 5 | 4/4 | 32.8 | 172079 |
| 6 | 6/6 | 51.5 | 399630 |

## Notes

- 6/6 evals pass 28/28 expectations. All results independently verified against ground truth (per-service call logs and direct JSON comparison of final stub state against seed fixtures), not executor self-report.
- This run replaces the 2026-07-31T04:27Z 3-eval Trello-only pilot baseline (83.3% pass). Two things changed since: (1) SKILL.md's Step 0 gained the sole-candidate scope-confirmation rule after the pilot's eval 1 failure — eval 1 now passes, with the executor surveying at board level only and explicitly asking before fetching card detail; (2) evals 4-6 were added covering the email workflow (Step 4b) and the capture-from-email-to-Trello flow (Step 4c), the latter running the Trello and Gmail stubs together in one trial.
- Executor mechanism (unchanged from the pilot): each trial is a real `claude -p --dangerously-skip-permissions --strict-mcp-config` subprocess against the mcp-stub servers, run from the user's authenticated terminal via `run-trials.sh`; see `evals/README.md`'s "MCP stub servers" section.
- Time and token figures are the subprocess's own reported values (`--output-format json`), not file-mtime approximations as in the pilot. The tokens figure is total tokens processed per trial (input + output + cache creation + cache read); cache reads dominate it, so it is NOT comparable to the subagent-token figures in other skills' baselines. Per-trial breakdowns live in the run's `metrics.json` artifacts (not committed).
- Continued good judgment observed beyond graded expectations: eval 2 re-flagged the fixture's "June conference" date ambiguity and asked rather than inventing a due date; eval 5 verified its empty-inbox result with one read-only `in:anywhere` query while explicitly declining to expand scope; eval 6 surfaced its due-date choice (fair date vs the PTA's "early September" request) as a question instead of silently deciding.
- Still deferred: Jira scope (needs a schema-verified Atlassian stub), staleness handling (Step 7 needs last-activity timestamps modeled in the stubs), and large-set batch pacing (Step 0.5).
