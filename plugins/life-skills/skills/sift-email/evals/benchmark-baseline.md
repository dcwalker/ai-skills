# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-26
**Evals**: 1-31 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 580/584 (99.3%): 291/292 run 1, 289/292 run 2 |
| Evals passing both runs | 27/31 |
| Time | 196.3s ± 85.5s |
| Tokens | 972,852 ± 497,468 (total processed, dominated by cache reads) |
| Tool calls | 31.3 ± 15.4 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial is one unattended `claude -p` turn against the Gmail, Claude Docs,
and Contacts stubs, and every eval checks that the run finishes without
waiting on the user. Graders checked labels, tabs, docs, and comments against
each stub's final state and call log, not the trial's reply.

This baseline covers the log-writing fixes (#135): log lines and changelog
entries name the user, run headings go directly above the previous newest
run, About me notes are recorded in the changelog, no log line holds an ID
number (including one in a copied subject), the Labels table covers every
`AI/` label in the account, and a new reply's earlier messages are read for
the user's tab. Both runs were on SKILL.md as of commit 0cce083, on
2026-10-25 in the fixtures' rubric timezone, with fixtures anchored to
2026-10-10 and shifted two weeks.

## What the evals found

Every eval passed in at least one run, and 27 of 31 passed in both.

The fixes held in both runs: no order numbers in the rubric or log, with
subjects copied without them (23); the user's tab kept on a new reply when an
earlier message was moved (27); a Labels table row for an `AI/` label sift
didn't create (30); run headings directly above the previous run (12, 21);
and About me notes recorded in the changelog (17). The voice leak in sift's
log reasons and summaries, 10 misses in the previous baseline, is gone.

Failures:

| Cause | Misses | Evals |
|-------|--------|-------|
| The user's first-person voice in a changelog entry, copied from user-voiced rubric wording ("unused until I say what goes there") | 2 | 30 run 2, 31 run 2 |
| Appended a second copy of the log template after a search read of the log came back empty, so the run heading sat under the copy | 1 | 18 run 2 |
| An About me note recorded how the user treats a sender's priority, counted as a learned rule | 1 | 7 run 1 |

Not graded, seen in a few trials: ID numbers in a log line outside eval 23
(eval 3 run 2's reason, eval 21 run 2's copied subject); run headings placed
above the Runs intro; log thread lines without the list marker, and changelog
entries using `date:` instead of `date |`; and category labels created up
front but never applied.

## Harness

- **Prompts.** Every eval prompt starts with `/sift-email`, followed by the
  rubric and log links (eval 1 gives none, for the first run).
- **Stubs and isolation** are unchanged from the previous baseline: Gmail,
  Claude Docs, and Contacts stubs; `run-mcp-trials.sh` turns off every plugin
  the developer has enabled, turns off auto-memory, and denies `WebFetch` in
  trials. Trial directories were under `$TMPDIR`. See evals/README.md.
- **Gmail stub.** `after:` and `before:` accept epoch seconds and compare
  against the thread's full timestamp.
- **Fixtures.** No fixture carries `AI/Important`, `AI/Needs reply`,
  `AI/Sifted`, or `AI/Wrong`; Important and needs-reply use `IMPORTANT` and
  `STARRED`. Log run headings carry their start as `{{epoch:...}}` tokens,
  which `fixture-dates.py` moves with the dates, and dates in message text
  in evals 18 and 19 are date tokens. Eval 11's already-ran entry uses
  `{{today:America/Chicago}}` and `{{todayepoch:...}}`, which follow the
  trial's own clock rather than the whole-week shift.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: create docs and labels | 10/10 | 10/10 | 158.7 | 177.0 | 28 | 39 | 965,834 | 918,422 |
| 2 | Sender context; star by message | 13/13 | 13/13 | 415.8 | 232.0 | 68 | 39 | 2,249,597 | 963,561 |
| 3 | Real purchase from label history | 9/9 | 9/9 | 132.0 | 125.6 | 19 | 20 | 529,530 | 532,449 |
| 4 | Bulk, Junk, and Low priority | 9/9 | 9/9 | 175.6 | 248.5 | 33 | 41 | 852,911 | 1,414,148 |
| 5 | Daily review reaches the threshold | 12/12 | 12/12 | 222.7 | 187.7 | 31 | 26 | 1,120,877 | 1,022,975 |
| 6 | Daily review: nothing is a signal | 10/10 | 10/10 | 218.3 | 208.3 | 32 | 31 | 857,284 | 820,812 |
| 7 | User's edits stand on new replies | 10/11 | 11/11 | 357.2 | 194.3 | 45 | 27 | 2,013,224 | 686,304 |
| 8 | Gmail's Important mark vs the user's | 8/8 | 8/8 | 171.9 | 191.7 | 19 | 22 | 689,897 | 709,137 |
| 9 | New reply in a sifted thread | 8/8 | 8/8 | 169.7 | 132.5 | 23 | 23 | 713,475 | 781,967 |
| 10 | Answered question applied | 8/8 | 8/8 | 131.6 | 123.3 | 26 | 20 | 818,732 | 609,786 |
| 11 | Nothing new: cheap exit | 7/7 | 7/7 | 63.4 | 42.9 | 12 | 13 | 384,966 | 354,168 |
| 12 | Archive granted for Junk | 7/7 | 7/7 | 174.6 | 109.6 | 33 | 26 | 1,116,308 | 685,272 |
| 13 | Archive asked, not granted | 8/8 | 8/8 | 106.2 | 160.7 | 26 | 22 | 670,153 | 786,941 |
| 14 | Docs connector missing | 7/7 | 7/7 | 69.0 | 63.1 | 20 | 19 | 439,379 | 492,361 |
| 15 | Oversized rubric consolidation | 10/10 | 10/10 | 347.2 | 205.6 | 22 | 20 | 1,059,198 | 840,598 |
| 16 | Existing marks are context | 9/9 | 9/9 | 159.7 | 146.9 | 34 | 26 | 835,645 | 660,824 |
| 17 | About me as memory | 11/11 | 11/11 | 160.8 | 159.9 | 32 | 35 | 1,018,254 | 1,133,519 |
| 18 | Whole-inbox backlog, two pages | 11/11 | 10/11 | 260.5 | 331.0 | 79 | 90 | 1,030,583 | 1,452,209 |
| 19 | Label the rubric asks for, under AI/ | 9/9 | 9/9 | 211.2 | 163.0 | 35 | 32 | 1,226,071 | 852,184 |
| 20 | Tidy About me into groups | 9/9 | 9/9 | 151.5 | 162.0 | 23 | 28 | 750,718 | 819,364 |
| 21 | Category labels by what a message is | 13/13 | 13/13 | 438.4 | 271.2 | 85 | 50 | 3,561,077 | 915,045 |
| 22 | Newsletters lists decide Bulk | 10/10 | 10/10 | 280.6 | 130.3 | 24 | 25 | 872,729 | 675,848 |
| 23 | Mail meant for the user, not Bulk | 11/11 | 11/11 | 228.0 | 220.4 | 37 | 40 | 1,383,737 | 1,441,313 |
| 24 | Newsletter reaches the threshold | 11/11 | 11/11 | 157.4 | 160.5 | 20 | 19 | 596,278 | 691,099 |
| 25 | Learned newsletter conflicts with the user's line | 9/9 | 9/9 | 249.9 | 159.4 | 32 | 23 | 1,189,521 | 851,046 |
| 26 | Tabs by the rubric, over Gmail | 12/12 | 12/12 | 260.4 | 187.7 | 48 | 34 | 1,744,508 | 943,083 |
| 27 | User-set tab vs Gmail's re-sort | 8/8 | 8/8 | 179.9 | 221.5 | 18 | 30 | 565,629 | 831,357 |
| 28 | Older rubric brought up to date | 10/10 | 10/10 | 460.1 | 362.6 | 42 | 35 | 1,682,708 | 1,652,113 |
| 29 | Evidence rewrites the user's rule | 8/8 | 8/8 | 170.4 | 204.0 | 24 | 20 | 822,409 | 672,561 |
| 30 | New Gmail tab added to the table | 8/8 | 7/8 | 190.8 | 135.2 | 25 | 22 | 975,914 | 770,855 |
| 31 | Rubric overrides skill defaults | 6/6 | 5/6 | 154.9 | 121.3 | 27 | 21 | 888,984 | 709,362 |
