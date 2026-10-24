# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-10-24T00:00:00Z
**Evals**: 1-41 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 94% ± 11% |
| Time | 105.5s ± 50.1s (n=41) |
| Tokens | 43314 ± 11243 (n=41) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 4/5 | 93.6 | 57426 |
| 2 | 4/4 | 53.9 | 31338 |
| 3 | 4/4 | 54.3 | 30238 |
| 4 | 3/4 | 122.5 | 41121 |
| 5 | 3/4 | 73.8 | 35153 |
| 6 | 5/5 | 74.4 | 38662 |
| 7 | 6/7 | 97.7 | 42363 |
| 8 | 5/5 | 60.9 | 33083 |
| 9 | 4/7 | 188.9 | 61198 |
| 10 | 5/5 | 59.2 | 33279 |
| 11 | 6/6 | 118.3 | 44719 |
| 12 | 5/5 | 60.1 | 31952 |
| 13 | 6/6 | 86.0 | 41214 |
| 14 | 6/7 | 80.4 | 38981 |
| 15 | 8/11 | 195.0 | 61845 |
| 16 | 4/4 | 13.9 | 22102 |
| 17 | 6/7 | 120.8 | 50001 |
| 18 | 6/7 | 135.2 | 54910 |
| 19 | 7/7 | 145.0 | 48812 |
| 20 | 3/4 | 12.6 | 23043 |
| 21 | 9/9 | 198.9 | 64782 |
| 22 | 11/12 | 192.6 | 63947 |
| 23 | 7/7 | 134.9 | 47787 |
| 24 | 7/7 | 137.8 | 48287 |
| 25 | 8/8 | 107.4 | 42655 |
| 26 | 8/8 | 210.9 | 65742 |
| 27 | 7/7 | 124.8 | 44533 |
| 28 | 11/11 | 127.1 | 48812 |
| 29 | 8/8 | 78.7 | 35124 |
| 30 | 5/5 | 196.8 | 58676 |
| 31 | 5/5 | 48.8 | 30457 |
| 32 | 7/7 | 123.5 | 43733 |
| 33 | 5/5 | 87.1 | 38015 |
| 34 | 7/7 | 91.8 | 37945 |
| 35 | 6/6 | 149.5 | 54055 |
| 36 | 6/6 | 64.1 | 33294 |
| 37 | 4/4 | 74.0 | 40291 |
| 38 | 4/4 | 92.9 | 45665 |
| 39 | 4/5 | 91.5 | 38221 |
| 40 | 5/5 | 84.5 | 37929 |
| 41 | 7/7 | 61.3 | 34476 |

## Notes

- 41 evals and 41 recorded runs pass 241/257 expectations, with 29 evals passing every expectation. Graders checked every claimed search, read, lookup, and card against the stub call logs, `events.jsonl`, `tools.log`, and saved workspace files rather than the executor's own report.
- This baseline accompanies [dcwalker/ai-skills#124](https://github.com/dcwalker/ai-skills/pull/124). The skill no longer bundles a Trello script: it creates tasks only when the user asks, in the tool the user names. It records sensitive topics and explicit language uncensored. It replaces the per-line interview and staged approval with filling gaps from the user's calendar, contacts, chat, trackers, and other notes, asking only about what no source settles, and it reports after the document what each source resolved.
- The previous baseline (2026-10-08) scored 219/233. Most of its expectations about the interview and approval flow were rewritten for this behavior (for example, "a per-line interview" became "no per-line interview"), so the two rates measure different things and are not directly comparable.
- New evals: 37 (a task request that names no tool), 38 (a task tool the skill cannot reach), 39 (censored profanity in a transcript), 40 (sensitive topics in a 1:1), and 41 (an initial, an attendance question, and a due date resolved from contacts and the calendar without asking).
- Evals 1, 4, 6, and 26 moved from the script's fixture hook to the Trello MCP stub. Eval 4's card failure uses the stub's new opt-in `create_card_errors` key.
- Eval 39 was regraded on review. Its grader passed the "no mask" expectation on a turn-2 edit, but the turn-1 document wrote "Priya reacted with an expletive" and said the word could not be restored. The word appeared only after the simulated user supplied it, so the row counts it as a failure.
- Known gaps accepted for this baseline:
  - Missing due dates still go unasked in 15 and 17. Eval 15 again ties a stated cutover timing to the ticket-filing action.
  - Eval 4 retried a failed card four times in one turn, against the no-retry rule.
  - Eval 20 did not look at the working directory or name `transcript.txt` before stopping.
  - Evals 9 and 15 add small connective facts and restate the chat message by message.
  - Eval 22 left out a join notice, and eval 1 reissued only the Action Items section after linking cards.
  - Eval 36's tentative-attendance default and eval 39's reported-speech wording passed in this run, after failing in earlier runs on this branch.
- Eval 15 attempted one write to `/tmp` for a word count, and the sandbox refused it; nothing reached outside the run directory.
- Harness changes this run used: the trial driver stops the simulated user on `DONE.` as well as `DONE` (before, a finished trial could run to the 40-turn cap), and the Trello script's fixture hook is gone.
- Run method: `evals/lib/run-mcp-trials.sh` with `SIMULATED_USER=1` (evals without `follow_ups` get a simulated user; the rest use their scripted follow-ups).
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
