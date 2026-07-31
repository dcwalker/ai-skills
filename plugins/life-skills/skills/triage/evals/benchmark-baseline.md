# Skill Benchmark: triage

**Model**: claude-sonnet-5
**Date**: 2026-07-31T04:27:00Z
**Evals**: 1-3 (1 run each, with_skill only, Trello-only pilot batch)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 83.3% ± 23.6% |
| Time | 37.7s ± 5.9s (n=3) |
| Tokens | unavailable (see notes) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 2/4 | 46 | n/a |
| 2 | 5/5 | 33 | n/a |
| 3 | 4/4 | 34 | n/a |

## Notes

- 2/3 evals pass all expectations; eval 1 fails 2 of its 4 expectations. All results were independently verified against ground truth (`trello-calls.log` call sequence and direct JSON comparison of `trello-state-out.json` against the seed fixture), not accepted from the transcript's self-report alone.
- Executor mechanism differs from every other skill's baseline in this repo: each trial is a real, separate `claude -p --dangerously-skip-permissions --strict-mcp-config` subprocess (via `evals/lib/mcp-stub/trello_stub.py` and `evals/lib/run-mcp-eval.sh`), not an in-process Agent-tool subagent, because MCP server resolution happens once at process launch and can't be swapped per-command via `PATH` the way the gh-stub is. See `evals/README.md`'s "MCP stub servers" section.
- Eval 1's failure is a genuine, repeatable finding, not a fixture artifact: given a vague scope request ("help me triage my backlog") against a Trello workspace containing exactly one board/list/card, the executor used Step 0's own "capability discovery" step to survey what exists, found only one candidate, and proceeded directly into a full per-item fetch and audit (`view_board`, `view_list`, `view_card`, `get_board_labels`) rather than stopping to ask the user to confirm scope first, as SKILL.md's Step 0 explicitly requires ("Do not proceed until scope is clear"). It did not mutate anything and did ask real clarifying questions, but only after already fetching full card detail — the ask came at the field level (due date, labels), not as the required scope-confirmation gate before touching card data. Worth a second opinion on whether Step 0 should be read as "ask only when genuinely ambiguous" rather than "always ask when the user didn't specify a target," since the current wording produced this divergence.
- Eval 2 surfaced a good example of correct judgment beyond what the eval anticipated: the fixture's card description says "the June conference" with no year, and the executor noticed this creates a real ambiguity against the session's current date (2026-07-30, so an unqualified "June conference" could mean a past or future date) and asked rather than inventing a due date — consistent with the skill's "never invent facts or dates" rule. This was graded as intended (correct) behavior, not a shortfall.
- Time figures are approximate, derived from file mtimes (`mcp-config.json` creation to `transcript.txt` completion) rather than the subprocess's own reported wall-clock time, since `run-trials.sh` invoked `claude -p` in plain-text output mode. Token figures are unavailable for the same reason (plain-text mode doesn't report usage) — a future run using `--output-format json` would capture both more precisely; not done here to avoid a second live round-trip for a 3-eval pilot batch.
- Scoped to triage's primary Trello-processing path (Steps 0-4, 8) with a single-board, Trello-only pilot fixture set. Step 4c's capture-into-Trello-from-another-platform flow, staleness handling (Step 7, which needs a last-activity timestamp the stub does not currently model), and Jira/Gmail scope are all deferred to a follow-up batch, not covered here.
