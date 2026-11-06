# Skill Benchmark: organize-meeting-notes

**Model**: claude-opus-5-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-11-06T00:00:00Z
**Evals**: 1-103 except 27 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 98% ± 8% |
| Time | 78.6s ± 25.6s (n=102) |
| Tokens | 50592 ± 7527 (n=102) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 4/4 | 105.7 | 64381 |
| 2 | 4/4 | 38.0 | 33790 |
| 3 | 4/4 | 83.1 | 47709 |
| 4 | 4/4 | 89.0 | 57035 |
| 5 | 2/2 | 58.6 | 46558 |
| 6 | 2/2 | 50.3 | 43194 |
| 7 | 4/4 | 64.7 | 50155 |
| 8 | 5/5 | 51.0 | 44889 |
| 9 | 4/5 | 115.1 | 57249 |
| 10 | 4/4 | 37.2 | 35195 |
| 11 | 5/5 | 79.5 | 54448 |
| 12 | 4/4 | 54.4 | 45272 |
| 13 | 5/5 | 67.1 | 50225 |
| 14 | 6/6 | 83.0 | 55396 |
| 15 | 8/9 | 116.8 | 65410 |
| 16 | 4/4 | 22.5 | 37361 |
| 17 | 3/3 | 85.0 | 62761 |
| 18 | 5/5 | 81.2 | 61058 |
| 19 | 6/6 | 71.6 | 47150 |
| 20 | 4/4 | 16.2 | 31136 |
| 21 | 6/6 | 107.5 | 53735 |
| 22 | 9/9 | 118.4 | 70647 |
| 23 | 5/5 | 87.4 | 52661 |
| 24 | 6/6 | 89.9 | 56973 |
| 25 | 6/6 | 98.2 | 54366 |
| 26 | 6/6 | 116.1 | 63812 |
| 28 | 8/8 | 101.7 | 56730 |
| 29 | 7/7 | 101.3 | 47453 |
| 30 | 5/5 | 102.1 | 52820 |
| 31 | 4/4 | 56.1 | 47748 |
| 32 | 7/7 | 59.0 | 46473 |
| 33 | 5/5 | 76.0 | 48106 |
| 34 | 6/6 | 84.4 | 49729 |
| 35 | 6/6 | 165.7 | 68951 |
| 36 | 4/4 | 72.7 | 47163 |
| 37 | 5/5 | 69.9 | 56622 |
| 38 | 4/4 | 59.7 | 50735 |
| 39 | 5/5 | 76.2 | 51593 |
| 40 | 5/5 | 77.1 | 48110 |
| 41 | 4/4 | 68.0 | 48645 |
| 42 | 5/5 | 52.4 | 38724 |
| 43 | 5/5 | 65.5 | 51348 |
| 44 | 4/4 | 58.8 | 38097 |
| 45 | 3/3 | 64.4 | 39859 |
| 46 | 3/3 | 67.7 | 44235 |
| 47 | 6/6 | 125.8 | 65728 |
| 48 | 5/5 | 66.5 | 47449 |
| 49 | 5/5 | 117.4 | 50142 |
| 50 | 6/6 | 126.2 | 49714 |
| 51 | 5/5 | 87.6 | 55541 |
| 52 | 6/6 | 80.9 | 54313 |
| 53 | 4/4 | 63.4 | 40674 |
| 54 | 6/6 | 70.4 | 53094 |
| 55 | 5/5 | 49.2 | 39270 |
| 56 | 4/4 | 55.8 | 49612 |
| 57 | 5/5 | 53.7 | 47180 |
| 58 | 5/5 | 54.5 | 48759 |
| 59 | 5/5 | 53.3 | 51997 |
| 60 | 5/5 | 84.8 | 58530 |
| 61 | 4/4 | 43.9 | 48341 |
| 62 | 2/2 | 84.4 | 52678 |
| 63 | 3/3 | 53.8 | 46384 |
| 64 | 1/1 | 50.0 | 43373 |
| 65 | 2/2 | 56.5 | 45785 |
| 66 | 3/3 | 105.9 | 57320 |
| 67 | 2/2 | 38.0 | 34527 |
| 68 | 3/3 | 72.2 | 46805 |
| 69 | 2/2 | 59.7 | 44955 |
| 70 | 2/2 | 76.4 | 50601 |
| 71 | 3/3 | 159.7 | 70123 |
| 72 | 2/2 | 78.5 | 58877 |
| 73 | 2/2 | 94.1 | 57304 |
| 74 | 3/3 | 100.0 | 60013 |
| 75 | 1/2 | 83.6 | 47401 |
| 76 | 2/3 | 71.9 | 46008 |
| 77 | 3/3 | 65.4 | 45307 |
| 78 | 3/3 | 66.8 | 45092 |
| 79 | 2/2 | 57.1 | 38814 |
| 80 | 2/2 | 73.7 | 51420 |
| 81 | 2/2 | 65.0 | 48926 |
| 82 | 7/7 | 52.7 | 52987 |
| 83 | 6/6 | 79.9 | 50938 |
| 84 | 6/6 | 84.5 | 49010 |
| 85 | 6/6 | 83.3 | 48181 |
| 86 | 6/6 | 73.6 | 51104 |
| 87 | 5/6 | 77.6 | 48631 |
| 88 | 6/6 | 66.7 | 46636 |
| 89 | 3/6 | 83.3 | 50836 |
| 90 | 7/7 | 128.0 | 60502 |
| 91 | 5/6 | 71.3 | 48281 |
| 92 | 8/8 | 84.7 | 51804 |
| 93 | 7/7 | 132.3 | 52182 |
| 94 | 7/7 | 76.3 | 52891 |
| 95 | 6/6 | 75.0 | 45225 |
| 96 | 6/6 | 99.9 | 48659 |
| 97 | 8/8 | 109.2 | 54882 |
| 98 | 8/8 | 89.5 | 51794 |
| 99 | 5/5 | 91.9 | 53759 |
| 100 | 4/4 | 89.7 | 52984 |
| 101 | 6/7 | 77.2 | 51594 |
| 102 | 4/4 | 78.5 | 52340 |
| 103 | 5/5 | 96.9 | 57445 |

## Notes

- 102 evals and 102 recorded runs pass 472/482 expectations, with 94 evals passing every expectation. Graders checked every claimed search, read, lookup, task, and file write against the stub call logs, `events.jsonl`, `tools.log`, and saved workspace files rather than the executor's own report.
- This baseline is not comparable to the 2026-11-05 baseline (361/375 on evals 1-61): this change splits the evals so each tests one behavior area, rewrites their expectations to be tool-neutral, drops eval 27, and adds evals 62-103.
- Evals 4 and 103 ran after the Step 7 retry change (three attempts in all, never waiting between them); the other evals ran before it, and none of them hits a failed task create. In both, the failing task was attempted exactly three times, with no sleep or scheduled retry.
- Known gaps accepted for this baseline:
  - Eval 9 adds the summary because of the section count, though the notes run about 285 words, short of the length band the expectation names.
  - Eval 15 leaves out Lena Fischer dropping off the call as logistics, though Step 5 keeps short logistics messages.
  - Eval 75 quotes a direct message the search showed only as context, and gives it a time (8:42 AM) that no bounded read supplied; its timestamp is 9:02 AM.
  - Eval 76 lists Marcus Hall, whose invite response was tentative, as absent with an offer to change it, rather than asking.
  - Evals 87, 89, and 91 give an attendee a pronoun no source states, against Step 5's pronoun rule.
  - Eval 89 puts the quoted fragment only in the pull quote, not inline in the note.
  - Eval 88 passes, but its lead-in still paraphrases the pull quote, as it did on the three earlier runs on this branch.
  - Eval 101 bounds the tracker search to the meeting's start and end, so it misses PLAT-211, created in the 15 minutes after the end, and never reports leaving it out.
- Run method: `evals/lib/run-mcp-trials.sh` with `SIMULATED_USER=1` and `TRIALS_DIR` under `$TMPDIR` (evals without `follow_ups` get a simulated user; the rest use their scripted follow-ups), on this branch. A search of every workspace for Claude Code session trailers found none.
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
