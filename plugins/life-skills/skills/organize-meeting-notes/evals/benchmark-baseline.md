# Skill Benchmark: organize-meeting-notes

**Model**: claude-opus-5-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-11-03T00:00:00Z
**Evals**: 1-50 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 96% ± 9% |
| Time | 64.1s ± 30.9s (n=50) |
| Tokens | 44299 ± 7718 (n=50) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 101.2 | 51448 |
| 2 | 4/4 | 18.5 | 29528 |
| 3 | 4/4 | 64.9 | 39967 |
| 4 | 3/4 | 73.1 | 53005 |
| 5 | 4/4 | 40.2 | 40981 |
| 6 | 5/5 | 46.4 | 37790 |
| 7 | 6/7 | 45.0 | 46661 |
| 8 | 5/5 | 36.8 | 38804 |
| 9 | 7/7 | 91.3 | 52029 |
| 10 | 5/5 | 26.9 | 31175 |
| 11 | 6/6 | 58.1 | 40016 |
| 12 | 5/5 | 33.9 | 38891 |
| 13 | 6/6 | 43.1 | 42672 |
| 14 | 7/7 | 43.7 | 39829 |
| 15 | 11/11 | 78.0 | 50700 |
| 16 | 4/4 | 21.4 | 34276 |
| 17 | 5/7 | 117.4 | 57136 |
| 18 | 7/7 | 77.5 | 54335 |
| 19 | 7/7 | 53.9 | 41321 |
| 20 | 4/4 | 16.3 | 26148 |
| 21 | 9/9 | 87.0 | 48618 |
| 22 | 12/12 | 93.6 | 55055 |
| 23 | 7/7 | 48.1 | 47813 |
| 24 | 6/7 | 93.1 | 51902 |
| 25 | 8/8 | 92.7 | 48554 |
| 26 | 5/8 | 140.6 | 58135 |
| 27 | 6/7 | 63.0 | 46373 |
| 28 | 11/11 | 107.2 | 53595 |
| 29 | 8/8 | 58.6 | 40314 |
| 30 | 5/5 | 77.7 | 50327 |
| 31 | 5/5 | 46.0 | 38677 |
| 32 | 7/7 | 51.6 | 39468 |
| 33 | 5/5 | 60.9 | 42561 |
| 34 | 7/7 | 80.5 | 44315 |
| 35 | 5/6 | 167.7 | 60201 |
| 36 | 5/6 | 64.0 | 40016 |
| 37 | 4/4 | 44.4 | 46994 |
| 38 | 3/4 | 49.6 | 44690 |
| 39 | 5/5 | 79.0 | 44153 |
| 40 | 5/5 | 61.4 | 41198 |
| 41 | 7/7 | 62.2 | 42239 |
| 42 | 6/6 | 34.1 | 41433 |
| 43 | 6/6 | 45.4 | 46421 |
| 44 | 5/5 | 37.5 | 32758 |
| 45 | 4/4 | 53.9 | 41057 |
| 46 | 5/5 | 103.6 | 48034 |
| 47 | 6/7 | 79.5 | 57394 |
| 48 | 5/5 | 21.6 | 31689 |
| 49 | 6/6 | 38.4 | 41457 |
| 50 | 6/6 | 74.1 | 42782 |

## Notes

- 50 evals and 50 recorded runs pass 294/307 expectations, with 40 evals passing every expectation. Graders checked every claimed search, read, lookup, card, and file write against the stub call logs, `events.jsonl`, `tools.log`, and saved workspace files rather than the executor's own report.
- This baseline accompanies [dcwalker/ai-skills#150](https://github.com/dcwalker/ai-skills/pull/150). The skill keeps a person's reply under a bot post, a blank-author Slack Connect message, a short logistics message, and a thread about another meeting; writes the chat disclosure line into every note; keeps a per-meeting checklist in a scratch directory during batch runs; captures Confluence pages attendees created or edited during the meeting; researches every person mentioned and applies likely names with evidence; and makes every question restate its meeting, quote, sources searched, and candidate.
- The executor changed from claude-sonnet-5 (the previous baseline, 2026-10-24, 241/257 on evals 1-41) to claude-opus-5-5, the trial driver's default on this run. On evals 1-41 this run scores 245/257. The two numbers span a model change as well as the skill change, so they are not directly comparable.
- New evals: 42 (a person's reply under a bot post), 43 (a Slack Connect reply whose author shows blank), 44 (a standup thread during an unrelated meeting), 45 (a one-line logistics direct message), 46 (the chat line in every saved note and a batch checklist), 47 (Confluence pages created, edited, edited only outside the window, and edited only by Loom), 48 (a likely name by title fit), 49 (a garbled name found through the org chart), and 50 (a question that restates its context). Before the skill change, the same model scored 33/51 on them; 42 to 45 failed then only because the chat line was not in the note, since the unchanged skill already kept each of those messages.
- Eight evals scored below the previous baseline on this run's first pass and were each re-run once. Evals 17, 24, 27, 35, 36, and 38 returned to their previous scores, and their rows above keep the first-pass result. Eval 29 quoted an out-of-window message in its "left out" list on both runs, a side effect of the new left-out listing; the listing was reworded to describe without quoting, and its row is the run on that final wording. Eval 26 left out REL-102 and REL-107 on both runs, and the unchanged skill on claude-opus-5-5 does the same, so that drop follows the model rather than this change.
- Every run except eval 29's used `SKILL.md` before that one-sentence rewording.
- Known gaps accepted for this baseline:
  - Eval 26 leaves out two Jira items created during the meeting.
  - Eval 35's first pass edited the Hiring Sync file's new chat line while finalizing, so the file no longer counted as unchanged; its re-run passed.
  - Eval 47 lists the included Confluence pages in the report without their links; the links appear only in the notes.
  - Eval 4 retried a failed card at the simulated user's request, against the no-retry rule.
  - Eval 49's `First (Last?)` expectation passed only because no draft was shown before the user confirmed the name.
- Run method: `evals/lib/run-mcp-trials.sh` with `SIMULATED_USER=1` and `TRIALS_DIR` under `$TMPDIR` (evals without `follow_ups` get a simulated user; the rest use their scripted follow-ups).
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
