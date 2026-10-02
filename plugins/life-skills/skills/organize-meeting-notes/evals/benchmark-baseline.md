# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-10-02T21:19:33Z
**Evals**: 1-25 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 92% ± 9% |
| Time | 147.9s ± 126.0s (n=25) |
| Tokens | 43309 ± 11328 (n=25) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 217.7 | 42407 |
| 2 | 4/4 | 43.0 | 29939 |
| 3 | 3/4 | 69.6 | 33236 |
| 4 | 3/4 | 103.6 | 38625 |
| 5 | 4/4 | 80.0 | 46230 |
| 6 | 5/5 | 204.9 | 40629 |
| 7 | 6/7 | 89.9 | 36970 |
| 8 | 5/5 | 321.8 | 32004 |
| 9 | 7/7 | 287.8 | 63736 |
| 10 | 5/5 | 73.6 | 34366 |
| 11 | 6/6 | 107.4 | 41831 |
| 12 | 4/5 | 66.3 | 33702 |
| 13 | 6/6 | 166.8 | 52800 |
| 14 | 7/7 | 123.8 | 53159 |
| 15 | 10/11 | 634.6 | 59213 |
| 16 | 4/4 | 12.7 | 22735 |
| 17 | 6/7 | 189.5 | 56840 |
| 18 | 6/7 | 135.5 | 59108 |
| 19 | 6/7 | 126.2 | 56295 |
| 20 | 3/4 | 12.6 | 22636 |
| 21 | 9/9 | 149.1 | 48766 |
| 22 | 11/12 | 113.9 | 48162 |
| 23 | 6/7 | 160.6 | 48681 |
| 24 | 5/6 | 97.8 | 38176 |
| 25 | 8/8 | 108.6 | 42491 |

## Notes

- 25 evals and 25 recorded runs pass 144/156 expectations, with 13 evals passing every expectation. Graders checked every claimed source check against the stub call logs and `events.jsonl` rather than the executor's own report, and found no claimed Slack read or search missing from the logs.
- This baseline accompanies issue #82. Step 1b's Team chat check now starts with a search bounded only by date, retries a refused timestamp-only search with an `on:` filter, reads each conversation it surfaced with the chat tool's own read bounded to the window, and opens its report with one `Chat:` line naming the window, the date terms, and the conversations read (or `nothing to read`).
- Run method matches the previous baseline: `evals/lib/run-mcp-trials.sh`, `claude -p` sessions limited to stub MCP servers, the skill's installed plugin turned off, evals 1-20 with `SIMULATED_USER=1` and evals 21-25 with scripted `follow_ups`. Every trial invoked the working-tree skill. The Slack stub changed in this PR: it now publishes the live tool's `keywords`, `filters`, and `natural_language_query`, honours `before`/`after` and `channel_types`, refuses a search with no terms, and logs every call, refused ones included.
- Eval 25 is new: in-window direct and group direct messages that share no keyword with the meeting, with keyword matches only outside the window. Evals 21, 22, and 23 gained expectations for the date-only search and the reported window, so their totals rose from 7, 10, and 5.
- On the previous baseline's own expectations for evals 1-24, this run scores 130/142 against 134/142. Evals 8 and 14 rose by one. Evals 4, 12, 15, 18, 19, and 24 each lost one, none in a rule this change touches: 4 made a third Trello call after the simulated user asked it to retry a failed card, graded literally here; 12 quoted a "close enough" phrase as Lena's words; 15 wrote "they" for proposals Lena and Dan made; 18 credited the referral bonus idea to Dan without support; 19 recorded the unreached docs freeze item as "never discussed" rather than open; 24 added "like the enforcement timeline" to the tracker note. An earlier full run on the PR's intermediate text failed 2, 9, and 13 instead and passed 18, 19, and 24, so single-run results move by several expectations either way.
- Every trial with Slack searched by date only first; none used a keyword or sender search as the check, including the empty-workspace evals that took that shortcut under the previous baseline. Evals 13 and 22 sent timestamp-only searches, were refused, and retried with `on:`. Every in-window conversation a search surfaced was read with `slack_read_channel`, and no trial claimed an unmade read.
- The `Chat:` line appeared and matched the call log in every Slack trial except eval 18, which reported the empty result in prose. Its form drifted often: bold or "Chat check:" labels, an added timezone or date, trailing commentary, and placement after a lead-in sentence rather than first. Only eval 4's line omitted the window.
- Eval 22 still drops Lena's join notice and Marcus's `:+1:`, and eval 23 still never asks what the bare link holds before the scripted follow-up answers it, as in the previous baseline.
- Not covered by any expectation: evals 22 and 25 asked another question instead of finalizing after "Finalize it"; eval 15 fetched a link found inside the chat log without asking; eval 13 wrote a memory file inside its trial home; eval 19 wrote `journal.md` to the real home directory by absolute path at the simulated user's request, which the harness did not detect (the file was removed).
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
