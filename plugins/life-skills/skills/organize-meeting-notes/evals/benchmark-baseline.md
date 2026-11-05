# Skill Benchmark: organize-meeting-notes

**Model**: claude-opus-5-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-11-05T00:00:00Z
**Evals**: 1-61 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 96% ± 8% |
| Time | 70.3s ± 25.9s (n=61) |
| Tokens | 48168 ± 8508 (n=61) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 97.4 | 56313 |
| 2 | 4/4 | 34.0 | 33777 |
| 3 | 4/4 | 62.3 | 43945 |
| 4 | 3/4 | 121.6 | 56680 |
| 5 | 4/4 | 53.2 | 36899 |
| 6 | 5/5 | 75.8 | 44309 |
| 7 | 7/7 | 72.1 | 45238 |
| 8 | 4/5 | 46.2 | 33841 |
| 9 | 6/7 | 135.1 | 55860 |
| 10 | 5/5 | 38.0 | 33955 |
| 11 | 5/6 | 123.5 | 50018 |
| 12 | 5/5 | 88.5 | 43241 |
| 13 | 6/6 | 46.5 | 50756 |
| 14 | 7/7 | 56.6 | 49897 |
| 15 | 11/11 | 87.9 | 60581 |
| 16 | 4/4 | 10.7 | 29937 |
| 17 | 5/7 | 68.2 | 57996 |
| 18 | 7/7 | 80.9 | 59024 |
| 19 | 7/7 | 59.6 | 53687 |
| 20 | 4/4 | 10.2 | 28991 |
| 21 | 9/9 | 78.1 | 54437 |
| 22 | 12/12 | 106.4 | 65514 |
| 23 | 7/7 | 55.7 | 49031 |
| 24 | 7/7 | 68.0 | 57291 |
| 25 | 8/8 | 72.7 | 52222 |
| 26 | 6/8 | 88.6 | 61338 |
| 27 | 7/7 | 67.1 | 53193 |
| 28 | 11/11 | 95.2 | 55705 |
| 29 | 8/8 | 76.2 | 45917 |
| 30 | 5/5 | 98.6 | 55239 |
| 31 | 5/5 | 53.4 | 43608 |
| 32 | 7/7 | 65.6 | 46025 |
| 33 | 5/5 | 72.4 | 45926 |
| 34 | 6/7 | 90.5 | 48307 |
| 35 | 6/6 | 157.0 | 66357 |
| 36 | 5/6 | 71.5 | 45407 |
| 37 | 4/4 | 72.4 | 54794 |
| 38 | 4/4 | 36.9 | 50662 |
| 39 | 4/5 | 57.1 | 45157 |
| 40 | 5/5 | 56.8 | 44821 |
| 41 | 7/7 | 65.3 | 43934 |
| 42 | 6/7 | 59.9 | 46285 |
| 43 | 6/6 | 59.9 | 47358 |
| 44 | 6/6 | 64.3 | 45414 |
| 45 | 4/4 | 62.1 | 36973 |
| 46 | 8/8 | 77.9 | 48965 |
| 47 | 6/7 | 95.3 | 61181 |
| 48 | 5/5 | 49.8 | 37736 |
| 49 | 6/6 | 66.2 | 49730 |
| 50 | 6/6 | 54.6 | 46294 |
| 51 | 5/5 | 69.7 | 55442 |
| 52 | 5/6 | 66.1 | 54901 |
| 53 | 6/6 | 51.3 | 37512 |
| 54 | 6/6 | 56.5 | 46545 |
| 55 | 5/5 | 53.2 | 39656 |
| 56 | 5/5 | 103.8 | 47627 |
| 57 | 5/5 | 60.2 | 35623 |
| 58 | 5/5 | 67.0 | 37253 |
| 59 | 5/5 | 87.9 | 50620 |
| 60 | 5/5 | 57.3 | 50813 |
| 61 | 10/10 | 54.9 | 52507 |

## Notes

- 61 evals and 61 recorded runs pass 361/375 expectations, with 49 evals passing every expectation. Graders checked every claimed search, read, lookup, card, and file write against the stub call logs, `events.jsonl`, `tools.log`, and saved workspace files rather than the executor's own report.
- This baseline records the skill as merged in [dcwalker/ai-skills#151](https://github.com/dcwalker/ai-skills/pull/151), including the Step 4 rewording that the previous baseline (2026-11-04) ran only on evals 52 and 55. Against that baseline's 358/375, evals 1, 7, 20, 22, 24, 48, 52, and 55 scored higher, and evals 8, 9, 11, 17, 34, 36, and 42 scored lower.
- The seven lower evals, and eval 52, which missed one expectation, were each re-run once. Evals 8, 9, 11, 34, 42, and 52 passed every expectation on the re-run, and their rows above keep the first-pass result. Eval 17 scored 6/7 and eval 36 scored 5/6 on the re-run.
- Known gaps accepted for this baseline:
  - Eval 36 struck Marcus Hall, whose invite response was tentative, as not attending on both runs, with an offer to change it rather than a question; Step 3 asks the user about an invitee whose attendance no source shows. The skill was left unchanged for this baseline.
  - Eval 17 attributes Speaker 3's quotes to an unidentified speaker on both runs, as on the previous baseline, and on its first pass did not ask for the macro cleanup's due date.
  - Evals 8 and 9 spelled out SLA from its usual meaning on their first pass after the term search found nothing, rather than asking; both passed on the re-run.
  - Eval 26 leaves out REL-102 and REL-107, created during the meeting, while the time zone is unconfirmed, as on the previous baseline.
  - Eval 47 reports the Confluence findings in prose, and lists the included pages without their links; the links appear only in the notes.
  - Eval 4 retried a failed card at the simulated user's request, against the no-retry rule.
  - Eval 39 describes Priya Raman's masked expletive rather than restoring a word, which the transcript does not give.
- Run method: `evals/lib/run-mcp-trials.sh` with `SIMULATED_USER=1` and `TRIALS_DIR` under `$TMPDIR` (evals without `follow_ups` get a simulated user; the rest use their scripted follow-ups), on `main` at the merge of #151. `check-trial-hygiene.sh` has nothing to check here, since this skill's workspaces are not git repositories; a search of every workspace for Claude Code session trailers found none.
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
