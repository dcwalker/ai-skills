# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-10-08T00:00:00Z
**Evals**: 1-36 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 93% ± 11% |
| Time | 125.1s ± 71.0s (n=36) |
| Tokens | 47966 ± 12507 (n=36) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 92.2 | 45037 |
| 2 | 4/4 | 60.3 | 35790 |
| 3 | 3/4 | 85.8 | 40741 |
| 4 | 3/4 | 178.5 | 49299 |
| 5 | 3/4 | 84.8 | 38302 |
| 6 | 5/5 | 78.8 | 39818 |
| 7 | 5/8 | 84.2 | 40993 |
| 8 | 5/5 | 95.3 | 38328 |
| 9 | 7/7 | 353.2 | 78369 |
| 10 | 5/5 | 102.0 | 43989 |
| 11 | 6/6 | 87.1 | 40069 |
| 12 | 5/5 | 82.3 | 38592 |
| 13 | 6/6 | 127.1 | 53857 |
| 14 | 5/7 | 151.0 | 49727 |
| 15 | 10/11 | 320.7 | 76648 |
| 16 | 4/4 | 15.0 | 27621 |
| 17 | 5/7 | 118.5 | 52692 |
| 18 | 7/7 | 248.1 | 84601 |
| 19 | 6/7 | 128.1 | 49422 |
| 20 | 3/4 | 19.7 | 28064 |
| 21 | 9/9 | 107.2 | 45710 |
| 22 | 11/12 | 175.8 | 63498 |
| 23 | 7/7 | 112.1 | 50045 |
| 24 | 7/7 | 113.7 | 46660 |
| 25 | 8/8 | 139.9 | 46883 |
| 26 | 8/8 | 240.0 | 61790 |
| 27 | 7/7 | 133.2 | 49079 |
| 28 | 9/11 | 128.4 | 51595 |
| 29 | 8/8 | 72.4 | 43250 |
| 30 | 5/5 | 153.2 | 56939 |
| 31 | 5/5 | 137.2 | 41026 |
| 32 | 7/7 | 68.9 | 37240 |
| 33 | 5/5 | 71.1 | 40393 |
| 34 | 7/7 | 113.2 | 45790 |
| 35 | 6/6 | 117.7 | 52344 |
| 36 | 6/6 | 105.3 | 42565 |

## Notes

- 36 evals and 36 recorded runs pass 217/233 expectations, with 25 evals passing every expectation. Graders checked every claimed search, read, and card against the stub call logs, `events.jsonl`, `tools.log`, and saved workspace files rather than the executor's own report.
- This baseline accompanies issue #96. Step 1b gains a source list, thread replies (each kept in its own block, a short reply read against its own parent, and a reply that continues a pre-meeting thread proposed as a follow-up with that parent as context), the timestamp-plus-date retry, a rule against reporting search-result context, and a timestamp search in place of a partial conversation listing. Step 3 replaces the roster with one line (who was invited, how many attended) when more than 20 attended or the names cannot all be established. Step 7 treats a request for the final document as approval of every pending stage. A Quality Rule covers re-checking work already produced.
- This run is the first without the identity leak: trials started from a Claude Code session had inherited the developer's account email through `CLAUDE_CODE_*` variables, which `evals/lib/isolation-env.sh` now unsets. An earlier full run on this branch with the leak scored 223/231; this one scores 217/233. On the 173 expectations shared with the 2026-10-07 baseline, it scores 159 against 161.
- New evals: 28 (thread replies, with a short reply that lands beside another thread's reply in time, and a follow-up on a pre-meeting thread), 29 (large account), 30 (attendee summary line), 31 (finalize on request), 32 (email), 33 (the 20-attendee boundary), 34 (listing fallback), 35 (re-checking a saved file), and 36 (connected calendar).
- Eval 28 was strengthened after the rest of this run, and the thread rules in Step 1b changed with it, so its row is the first of three runs on the final text (9/11, 11/11, 10/11). No other eval's fixture has thread replies, so the rest of the run is unaffected by that change. Across nine runs since the thread rule was first strengthened, the final notes kept every reply with its own thread; the remaining failures are in how the first proposal lays out the threads, which one run in three still flattened into a single time-ordered list.
- Failures elsewhere include runs that ended before a final document (7), a missing agenda-item link (7), the summary rule (14), drafting without asking for every due date (15), and an unconfirmed action item (22). Eval 27's Trello fixture now pins `stub_now`; without it, the case passed or failed by run date, and it failed on main as well.
- Harness changes this run used: the Slack stub returns thread replies from search, pages, lists conversations, and can refuse search; the Gmail stub supports `OR`, phrases, and parentheses; a calendar stub is new; trials get an explicit `--tools` set, the driver stops on a login failure, and the host account's identity variables are unset.
- Run method: `evals/lib/run-mcp-trials.sh` with `SIMULATED_USER=1` (evals without `follow_ups` get a simulated user; the rest use their scripted follow-ups).
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
