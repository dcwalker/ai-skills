# Skill Benchmark: organize-meeting-notes

**Model**: claude-opus-5-5 (executor) / claude-opus-5-5 (analyzer)
**Date**: 2026-11-04T00:00:00Z
**Evals**: 1-61 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 95% ± 11% |
| Time | 93.6s ± 77.4s (n=61) |
| Tokens | 46742 ± 8140 (n=61) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 4/5 | 147.6 | 64419 |
| 2 | 4/4 | 37.9 | 32583 |
| 3 | 4/4 | 83.3 | 46188 |
| 4 | 3/4 | 104.8 | 55598 |
| 5 | 4/4 | 50.9 | 35672 |
| 6 | 5/5 | 65.9 | 41629 |
| 7 | 6/7 | 77.2 | 45836 |
| 8 | 5/5 | 47.6 | 42982 |
| 9 | 7/7 | 138.6 | 52979 |
| 10 | 5/5 | 45.6 | 41331 |
| 11 | 6/6 | 77.3 | 48504 |
| 12 | 5/5 | 66.2 | 43678 |
| 13 | 6/6 | 75.0 | 52249 |
| 14 | 7/7 | 46.8 | 54332 |
| 15 | 11/11 | 93.7 | 55139 |
| 16 | 4/4 | 11.7 | 28426 |
| 17 | 6/7 | 107.5 | 58713 |
| 18 | 7/7 | 73.0 | 55237 |
| 19 | 7/7 | 30.1 | 36556 |
| 20 | 3/4 | 21.7 | 29015 |
| 21 | 9/9 | 139.1 | 54070 |
| 22 | 11/12 | 148.8 | 65587 |
| 23 | 7/7 | 141.4 | 47519 |
| 24 | 6/7 | 175.9 | 49045 |
| 25 | 8/8 | 159.4 | 49581 |
| 26 | 6/8 | 583.8 | 59094 |
| 27 | 7/7 | 104.4 | 49304 |
| 28 | 11/11 | 145.3 | 52904 |
| 29 | 8/8 | 73.6 | 44176 |
| 30 | 5/5 | 131.3 | 52223 |
| 31 | 5/5 | 46.6 | 43803 |
| 32 | 7/7 | 71.3 | 43088 |
| 33 | 5/5 | 94.7 | 43266 |
| 34 | 7/7 | 81.1 | 46351 |
| 35 | 6/6 | 235.5 | 57307 |
| 36 | 6/6 | 84.8 | 43920 |
| 37 | 4/4 | 113.4 | 54200 |
| 38 | 4/4 | 72.2 | 49081 |
| 39 | 4/5 | 116.5 | 50314 |
| 40 | 5/5 | 34.0 | 34554 |
| 41 | 7/7 | 63.0 | 44746 |
| 42 | 7/7 | 101.1 | 35941 |
| 43 | 6/6 | 116.0 | 35239 |
| 44 | 6/6 | 143.7 | 34162 |
| 45 | 4/4 | 169.7 | 44032 |
| 46 | 8/8 | 58.3 | 39054 |
| 47 | 6/7 | 102.3 | 60457 |
| 48 | 4/5 | 38.0 | 42294 |
| 49 | 6/6 | 86.0 | 49614 |
| 50 | 6/6 | 69.3 | 46884 |
| 51 | 5/5 | 47.7 | 48315 |
| 52 | 3/6 | 44.1 | 48206 |
| 53 | 6/6 | 39.5 | 37229 |
| 54 | 6/6 | 49.9 | 42060 |
| 55 | 3/5 | 73.4 | 46681 |
| 56 | 5/5 | 63.8 | 47009 |
| 57 | 5/5 | 39.2 | 38545 |
| 58 | 5/5 | 56.1 | 46010 |
| 59 | 5/5 | 62.7 | 52851 |
| 60 | 5/5 | 73.3 | 54709 |
| 61 | 10/10 | 59.3 | 46782 |

## Notes

- 61 evals and 61 recorded runs pass 358/375 expectations, with 48 evals passing every expectation. Graders checked every claimed search, read, lookup, card, and file write against the stub call logs, `events.jsonl`, `tools.log`, and saved workspace files rather than the executor's own report.
- This baseline accompanies [dcwalker/ai-skills#151](https://github.com/dcwalker/ai-skills/pull/151). The skill weaves chat into the notes as verbatim exchanges and keeps the chat disclosure line in the report only; researches names, acronyms, codenames, and terms in chat, Confluence, Jira, email, contacts, and earlier notes before asking; quotes for emotion and reaction, with pull quotes for heavy text, review, and short punchy lines; drops the journal destination; adds a self-contained HTML version with a CSS-only palette picker that follows the browser's light or dark mode; and moves time arithmetic, Notes measurement, and HTML rendering into scripts.
- On evals 1-50 this run scores 300/312, against 294/307 on the previous baseline (2026-11-03). Evals 11, 28, 39, and 42-46 had expectations rewritten for the chat, quote, and HTML changes, so the totals are not directly comparable.
- New evals: 51 (an owner found on a Confluence page), 52 (a short name that is not the attendee it matches, found in earlier notes or Jira), 53 (pronouns from a profile, a discussion confirmed in the transcript, and a weekday due date), 54 (an acronym defined in Slack), 55 (a codename defined in email), 56 (a misspelled name found in window chat), 57 (misspelled attendees corrected from the calendar), 58 (a person found through contacts relationships), 59 (an acronym with conflicting definitions, which is asked about), 60 (an acronym no source mentions, which is asked about), and 61 (an HTML version offered for a single meeting). They score 58/63 on this run; the unchanged skill was not run on them.
- Seven evals scored below the previous baseline or failed a new expectation on this run's first pass, and were each re-run once. Evals 1, 20, 22, 48, 52, and 55 passed every expectation on the re-run, and their rows above keep the first-pass result. Eval 39 scored 4/5 on both runs, failing a different expectation each time.
- Known gaps accepted for this baseline:
  - Evals 52 and 55 skipped the subject search from any date on their first pass: 52 never searched earlier notes or Jira by subject and took "ben" for the attendee Benjamin Ito, and 55 bounded its Gmail search for "Kestrel" to the meeting week and asked the user instead. Both re-runs searched without a date bound and passed. Step 4 was then reworded: a short form matching an attendee is not settled by the attendee list, and a term search runs on its own with no date bound. On that wording, 52 and 55 were each run twice more and passed every expectation all four times (52: 6/6, 6/6; 55: 5/5, 5/5).
  - Eval 39 hesitated over Priya Raman's masked expletive on both runs, whose word the transcript does not give, and on the re-run quoted Marcus Hall's line inline rather than as a pull quote, which the new quote guidance allows.
  - Eval 26 leaves out REL-102 and REL-107, created during the meeting, while the time zone is unconfirmed, as on the previous baseline.
  - Eval 47 lists the included Confluence pages in the report without their links; the links appear only in the notes.
  - Eval 4 retried a failed card at the simulated user's request, against the no-retry rule.
  - Eval 17 attributes Speaker 3's quotes to an unidentified speaker.
  - Eval 7 links the roadmap doc without a summary, since the simulated user did not have its contents.
  - Eval 24 never asks what the dependency tracker holds.
- Every run except the four extra runs of evals 52 and 55 used `SKILL.md` before the Step 4 rewording.
- Run method: `evals/lib/run-mcp-trials.sh` with `SIMULATED_USER=1` and `TRIALS_DIR` under `$TMPDIR` (evals without `follow_ups` get a simulated user; the rest use their scripted follow-ups). `check-trial-hygiene.sh` has nothing to check here, since this skill's workspaces are not git repositories; a search of every workspace for Claude Code session trailers found none.
- Tokens are input, output, and cache-creation tokens summed across every turn of the `claude -p` session, excluding cache reads, the same measure as the previous baseline.
