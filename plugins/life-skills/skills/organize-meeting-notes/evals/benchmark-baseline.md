# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-10-08T00:00:00Z
**Evals**: 1-36 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 97% ± 7% |
| Time | 121.9s ± 53.4s (n=36) |
| Tokens | 46433 ± 10087 (n=36) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 104.1 | 42235 |
| 2 | 4/4 | 58.0 | 33964 |
| 3 | 3/4 | 130.3 | 40191 |
| 4 | 3/4 | 156.7 | 47538 |
| 5 | 4/4 | 108.4 | 41229 |
| 6 | 5/5 | 206.8 | 45474 |
| 7 | 7/8 | 181.1 | 44354 |
| 8 | 5/5 | 83.0 | 39775 |
| 9 | 7/7 | 218.2 | 67756 |
| 10 | 5/5 | 76.0 | 34750 |
| 11 | 6/6 | 103.5 | 43291 |
| 12 | 5/5 | 196.3 | 42324 |
| 13 | 6/6 | 107.3 | 47280 |
| 14 | 6/7 | 151.9 | 50350 |
| 15 | 10/11 | 204.5 | 62893 |
| 16 | 4/4 | 9.9 | 26909 |
| 17 | 6/7 | 136.6 | 58721 |
| 18 | 7/7 | 166.6 | 63352 |
| 19 | 6/7 | 153.1 | 50995 |
| 20 | 4/4 | 27.4 | 29045 |
| 21 | 9/9 | 120.8 | 47822 |
| 22 | 11/12 | 197.9 | 66951 |
| 23 | 7/7 | 88.9 | 45058 |
| 24 | 7/7 | 104.9 | 42611 |
| 25 | 8/8 | 132.0 | 50585 |
| 26 | 8/8 | 176.9 | 63107 |
| 27 | 7/7 | 113.4 | 48837 |
| 28 | 9/9 | 126.6 | 53012 |
| 29 | 8/8 | 62.0 | 38555 |
| 30 | 5/5 | 170.2 | 51884 |
| 31 | 5/5 | 47.0 | 35503 |
| 32 | 7/7 | 59.8 | 37988 |
| 33 | 5/5 | 68.3 | 41256 |
| 34 | 7/7 | 102.2 | 43518 |
| 35 | 6/6 | 155.8 | 54072 |
| 36 | 6/6 | 80.0 | 38399 |

## Notes

- 36 evals and 36 recorded runs pass 223/231 expectations, with 28 evals passing every expectation. Graders checked every claimed search, read, and card against the stub call logs, `events.jsonl`, `tools.log`, and saved workspace files rather than the executor's own report.
- This baseline accompanies issue #96. Step 1b gains a source list, thread replies, the timestamp-plus-date retry, a rule against reporting search-result context, and a timestamp search in place of a partial conversation listing. Step 3 replaces the roster with one line (who was invited, how many attended) when more than 20 attended or the names cannot all be established. Step 7 treats a request for the final document as approval of every pending stage. A Quality Rule covers re-checking work already produced.
- New evals: 28 (thread replies), 29 (large account), 30 (attendee summary line), 31 (finalize on request), 32 (email), 33 (the 20-attendee boundary), 34 (listing fallback), 35 (re-checking a saved file), and 36 (connected calendar). All nine pass every expectation on this run. Earlier drafts failed them: an executor dropped the timestamp bounds when adding a date filter and reported chat empty (29), gave a search-context message an invented time (29), merged two threads' replies (28), and ended runs before a final document (21, 24, 25, 26, 28, 29), each fixed in the text or the follow-ups.
- On the 173 expectations shared with the previous baseline, this run scores 165 against 161: up in 14, 15, 18 (three), and 20, down in 7 (the roadmap note lost its link, which stayed in the Agenda) and 19 (the docs freeze date not marked open). Eval 27's Trello fixture now pins `stub_now`; without it, the case passed or failed by run date, and it failed on main as well.
- Harness changes this run used: the Slack stub returns thread replies from search, pages, lists conversations, and can refuse search; the Gmail stub supports `OR`, phrases, and parentheses; a calendar stub is new; trials get an explicit `--tools` set, and the driver stops on a login failure.
- Run method: `evals/lib/run-mcp-trials.sh` with `SIMULATED_USER=1` (evals without `follow_ups` get a simulated user; the rest use their scripted follow-ups), every eval run on the final text and harness.
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
