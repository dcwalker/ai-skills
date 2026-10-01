# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-10-01T23:48:24Z
**Evals**: 1-24 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 94% ± 9% |
| Time | 114.5s ± 58.5s (n=24) |
| Tokens | 41331 ± 12237 (n=24) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 210.0 | 35577 |
| 2 | 4/4 | 45.3 | 23320 |
| 3 | 3/4 | 66.0 | 31133 |
| 4 | 4/4 | 130.1 | 44016 |
| 5 | 4/4 | 71.7 | 33831 |
| 6 | 5/5 | 89.2 | 33105 |
| 7 | 6/7 | 219.9 | 39714 |
| 8 | 4/5 | 72.4 | 41925 |
| 9 | 7/7 | 251.6 | 74858 |
| 10 | 5/5 | 74.1 | 32112 |
| 11 | 6/6 | 73.2 | 33699 |
| 12 | 5/5 | 57.6 | 32060 |
| 13 | 6/6 | 145.1 | 45049 |
| 14 | 6/7 | 118.8 | 44262 |
| 15 | 11/11 | 174.3 | 60105 |
| 16 | 4/4 | 11.8 | 21555 |
| 17 | 6/7 | 117.9 | 51127 |
| 18 | 7/7 | 150.8 | 57306 |
| 19 | 7/7 | 136.2 | 47558 |
| 20 | 3/4 | 64.3 | 28570 |
| 21 | 7/7 | 124.4 | 46260 |
| 22 | 9/10 | 137.9 | 51951 |
| 23 | 4/5 | 126.9 | 45855 |
| 24 | 6/6 | 79.8 | 36999 |

## Notes

- 24 evals and 24 recorded runs pass 134/142 expectations, with 16 evals passing every expectation. Results were verified against ground truth rather than executor self-report: grader subagents checked card URLs and call counts against `trello-calls.log` and every claimed source check against the stub call logs, and found no claimed tool call missing from the logs.
- This baseline accompanies issue #80: Step 1b makes every reachable source mandatory, Team chat reads every direct message, group direct message, and attendee channel inside the meeting's actual window, a chat message about the recording becomes the italic note under the metadata, and Shared links skips summaries a link's own text already provides and asks what an unreadable link holds.
- The run method changed, so these figures are not directly comparable with the previous baseline (124/128 over 22 runs of evals 1-20). Trials ran through `evals/lib/run-mcp-trials.sh` as `claude -p` sessions limited to stub MCP servers, with the skill's installed plugin turned off so the working tree was measured. Evals 1-20 used `SIMULATED_USER=1`, a tool-less second session playing the user from the eval's prompt alone; evals 21-24 used scripted `follow_ups`. The previous Agent-tool executors and simulated user are no longer safe here, because a subagent sees the session's real connected sources and Step 1b now consults them.
- Evals 1-20 each carry an empty Slack stub, the minimum the MCP driver needs; eval 8's first expectation was reworded for it.
- Evals 21-24 are new: 21 (a one-to-one whose transcript stops because the other attendee asked by direct message for the recording to stop), 22 (side conversations in a channel, direct messages, and a group direct message, with a bot post and out-of-window messages), 23 (self-explanatory links beside an unresolvable one), and 24 (a Confluence page that returns an empty body).
- Against the previous baseline's first recorded run of each eval (112/114 for evals 1-20), this run scores 108/114. Eval 15 rose from 9/11 to 11/11. Evals 3, 7, 8, 14, 17, and 20 each lost one expectation, none in rules this change touches: 3 never reached the Trello question because the simulated user declined early; 7 left the roadmap link only in the Agenda section; 8 asked about both note lines in one message; 14's summary turned "backfill approved" into "backfilled", the summary-fidelity issue the previous baseline recorded for eval 9; 17 drafted from artifacts without asking; 20 never named the transcript it found, after a simulated user that reversed its own "just stop there".
- Eval 23 never asked what the unresolvable link holds, because the scripted follow-up supplied the answer before the skill reached that line. Eval 22 dropped Lena's join notice without mention.
- With an empty Slack workspace, trials in evals 1, 4, 7, 8, 15, 17, and 23 searched by keyword, sender, or whole day rather than reading the meeting window; evals 21 and 22, where chat held messages, followed the rule. The empty workspace hid the gap, so no expectation failed on it.
- The simulated user invented details its opening prompt did not support in several runs (evals 9, 14, 15, 17, and 19) and reversed itself in eval 20. Graders separated those from skill behavior. `conversation.txt` and the simulated user see only each turn's final message, so a question asked earlier in a turn can be missed; graders checked `events.jsonl` where that mattered.
- Not covered by any expectation: eval 7 searched the whole filesystem for `create-trello-task.sh`, timed out, and finalized without asking about Trello; eval 12 kept a paraphrase in quotation marks marked "(paraphrased)"; eval 24 replaced the user's Confluence URL with the API's tiny link.
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, so they are not comparable with the previous baseline's per-subagent figures.
