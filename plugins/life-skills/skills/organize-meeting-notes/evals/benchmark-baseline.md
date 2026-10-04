# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-10-04T00:00:00Z
**Evals**: 1-25 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 91% ± 13% |
| Time | 105.3s ± 59.4s (n=25) |
| Tokens | 46823 ± 12903 (n=25) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 136.8 | 51296 |
| 2 | 4/4 | 43.8 | 34202 |
| 3 | 3/4 | 54.1 | 36116 |
| 4 | 3/4 | 115.3 | 39343 |
| 5 | 3/4 | 54.8 | 36605 |
| 6 | 5/5 | 86.3 | 38617 |
| 7 | 7/8 | 75.4 | 40435 |
| 8 | 5/5 | 72.5 | 39334 |
| 9 | 5/7 | 257.8 | 73572 |
| 10 | 4/5 | 34.9 | 32547 |
| 11 | 6/6 | 85.3 | 41165 |
| 12 | 5/5 | 77.3 | 39264 |
| 13 | 6/6 | 113.5 | 52492 |
| 14 | 7/7 | 117.9 | 47588 |
| 15 | 9/11 | 260.6 | 79187 |
| 16 | 4/4 | 13.0 | 27317 |
| 17 | 7/7 | 116.0 | 56840 |
| 18 | 6/7 | 134.3 | 60147 |
| 19 | 7/7 | 126.3 | 54412 |
| 20 | 2/4 | 78.9 | 39866 |
| 21 | 9/9 | 98.2 | 47322 |
| 22 | 11/12 | 184.6 | 67324 |
| 23 | 7/7 | 110.7 | 47724 |
| 24 | 7/7 | 67.3 | 37359 |
| 25 | 8/8 | 117.0 | 50498 |

## Notes

- 25 evals and 25 recorded runs pass 145/158 expectations, with 15 evals passing every expectation. Graders checked every claimed source check, fetch, and card against the stub call logs, `events.jsonl`, and `tools.log` rather than the executor's own report.
- This baseline accompanies issue #83. A new `life-skills` `bin/create-trello-task.sh` shim puts the Trello script on PATH in an installed plugin, mirroring the software-development shims, and Step 7 falls back to the bundled `scripts/create-trello-task.sh` relative to SKILL.md, never searching the filesystem; a script that cannot be run is reported. The URL rule keeps each link as the user gave it. A new always-on paraphrase rule writes an approximation as reported speech, never in quotation marks with or without a label.
- Run method matches the previous baseline: `evals/lib/run-mcp-trials.sh`, `claude -p` sessions limited to stub MCP servers, the skill's installed plugin turned off, evals 1-20 with `SIMULATED_USER=1` and evals 21-25 with scripted `follow_ups`. Every trial invoked the working-tree skill. Trials ran in two parallel batches.
- Eval 12's quote expectation now fails a paraphrase kept in quotation marks with a "(paraphrased)" label, eval 24 gained a check that both Confluence links stay as the user gave them, and eval 7 gained a check that the Trello question is asked and an unrunnable script is reported. Eval 7 and 24 totals rose from 7 and 6.
- On the 155 expectations the two baselines share, this run scores 142 against 144. Evals 17, 19, 23, and 24 rose by one; evals 5, 10, 15, and 20 lost one and eval 9 two, none in a rule this change touches: 5 accepted the simulated user's claim that the duration, not the end time, was mistyped; 9 summarized with "and"-chained sentences and skipped a line (below); 10 ended on its first approval question without a final document; 15 assigned the runbook update to Priya without asking; 20's simulated user pasted its own notes instead of following the scenario. The earlier baseline's own note applies: single runs move by several expectations either way.
- The targeted behaviors: eval 12 kept "flying blind" out of quotation marks and passed every expectation; eval 24 kept both Confluence URLs exactly, using neither the tool's `webui` nor `tinyui` link; eval 7's new Trello expectation passed only because the simulated user confirmed no action items, so the question it targets was not exercised. No trial in the suite put a paraphrase in quotation marks in a final document or replaced a URL.
- Eval 8's per-line interview, which the issue flagged, passed here and in three separate reruns on the previous text, each asking about one raw line per message, so the interview wording is unchanged.
- The Trello script ran only where the user wanted cards, in evals 4 and 6. Eval 4's planned card failure was reported, and retried at the simulated user's request. Eval 1 still ran `find / -maxdepth 6` for the skill directory before using the bundled script, and eval 4 a Glob for it, despite Step 7's new rule against searching.
- Eval 9's executor wrote a question for line 15 and an answer to it inside its own turn, made a stray `Read` of a nonexistent path, and when the simulated user pointed out the skipped line, said it had already been answered; the line's final note rests on that invented answer. It is the only fabrication found across the suite and is not tied to this change, but it is the most serious finding here.
- Not covered by any expectation: evals 4 and 6 created cards on the user's up-front approval without first asking "Are these action items correct?"; evals 1 and 6 combined one line's proposed wording with the next line's question in a single message; evals 17 and 19 searched the home and root directories for a journal folder; eval 20 never checked the connected Slack workspace; several trials named the user "Dan Walker" from the recording machine's account context, which reached the trials despite the harness's isolation.
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
