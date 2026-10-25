# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-25
**Evals**: 1-31 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 563/576 (97.7%): 280/288 run 1, 283/288 run 2 |
| Evals passing both runs | 20/31 |
| Time | 188.9s ± 76.4s |
| Tokens | 910,570 ± 393,968 (total processed, dominated by cache reads) |
| Tool calls | 30.6 ± 15.3 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial is one unattended `claude -p` turn against the Gmail, Claude Docs,
and Contacts stubs, and every eval checks that the run finishes without
waiting on the user. Graders checked labels, tabs, docs, and comments against
each stub's final state and call log, not the trial's reply.

This baseline covers inbox tabs filed by the rubric (#131), label searches by
name (#115), the first-person check (#112), the judgment rules moved from
SKILL.md into the rubric, and the rubric as one living document sift keeps
accurate, with rubric lines in the user's voice and reports naming the user.
Both runs were on SKILL.md as of commit 0b8798f, on 2026-10-25 in the
fixtures' rubric timezone, with fixtures anchored to 2026-10-10 and shifted
two weeks.

## What the evals found

Every eval passed in at least one run, and 20 of 31 passed in both.

The new behavior held in both runs: threads filed into tabs by the rubric's
Tabs table over Gmail's sort (26), a tab the user set kept on a new reply
(27), Gmail's Important mark told apart from the user's (8), an older rubric
folded into the new layout with its tables and how-to updated (28), evidence
rewriting a rule the user wrote (29), a new Gmail tab added to the Tabs table
(30), the rubric overriding the skill's old defaults (31), no account digits in
About me (13), and label searches by name (3).

Failures:

| Cause | Misses | Evals |
|-------|--------|-------|
| The user's first-person voice in sift's log reasons, run summaries, or changelog ("nothing asked of me") | 10 | 3, 4, 5, 16, 18, 19 (both runs), 21, 25, 30 |
| Deleted 22 narrow sender rules as covered by the user's general automated-notifications rule, rather than consolidating them | 2 | 15 run 1 |
| Read the whole rubric before the Step 2 checks | 1 | 11 run 1 |

The voice misses share one cause: Step 7, where sift writes the log, does not
restate that reports name the user, so lines copy the rubric's own wording.

Not graded, seen in a few trials: run headings placed below an older run or
above the Runs intro, and one run (eval 21) with no heading; About me notes
added without a changelog entry; order numbers in some About me notes and log
lines; newsletters filed in Primary rather than the Tabs table's tab; and
category labels created up front but never applied.

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
| 1 | First run: create docs and labels | 10/10 | 10/10 | 149.7 | 165.3 | 28 | 36 | 809,987 | 790,564 |
| 2 | Sender context; star by message | 13/13 | 13/13 | 223.3 | 296.5 | 42 | 49 | 833,216 | 1,797,864 |
| 3 | Real purchase from label history | 8/9 | 9/9 | 247.2 | 123.2 | 24 | 19 | 823,399 | 481,079 |
| 4 | Bulk, Junk, and Low priority | 9/9 | 8/9 | 173.1 | 158.1 | 32 | 28 | 849,549 | 734,842 |
| 5 | Daily review reaches the threshold | 12/12 | 11/12 | 200.8 | 185.4 | 24 | 21 | 788,108 | 698,533 |
| 6 | Daily review: nothing is a signal | 10/10 | 10/10 | 181.2 | 195.0 | 27 | 28 | 630,592 | 725,194 |
| 7 | User's edits stand on new replies | 11/11 | 11/11 | 353.4 | 256.3 | 42 | 38 | 1,859,544 | 1,626,126 |
| 8 | Gmail's Important mark vs the user's | 8/8 | 8/8 | 313.6 | 177.3 | 39 | 26 | 1,774,159 | 726,168 |
| 9 | New reply in a sifted thread | 8/8 | 8/8 | 162.9 | 256.3 | 26 | 26 | 903,348 | 925,235 |
| 10 | Answered question applied | 8/8 | 8/8 | 144.2 | 154.5 | 22 | 18 | 809,693 | 574,932 |
| 11 | Nothing new: cheap exit | 6/7 | 7/7 | 52.0 | 51.7 | 14 | 12 | 398,606 | 380,445 |
| 12 | Archive granted for Junk | 6/6 | 6/6 | 174.3 | 134.6 | 32 | 27 | 1,090,236 | 867,460 |
| 13 | Archive asked, not granted | 8/8 | 8/8 | 106.9 | 133.4 | 25 | 27 | 549,274 | 718,169 |
| 14 | Docs connector missing | 7/7 | 7/7 | 58.7 | 57.0 | 17 | 19 | 511,800 | 412,052 |
| 15 | Oversized rubric consolidation | 8/10 | 10/10 | 269.4 | 280.2 | 18 | 18 | 770,240 | 700,821 |
| 16 | Existing marks are context | 8/9 | 9/9 | 147.4 | 168.1 | 29 | 31 | 751,227 | 834,658 |
| 17 | About me as memory | 10/10 | 10/10 | 163.0 | 203.7 | 35 | 36 | 774,905 | 1,279,701 |
| 18 | Whole-inbox backlog, two pages | 11/11 | 10/11 | 380.5 | 295.8 | 98 | 94 | 2,408,480 | 1,502,676 |
| 19 | Label the rubric asks for, under AI/ | 8/9 | 8/9 | 200.4 | 202.7 | 40 | 29 | 1,037,638 | 946,883 |
| 20 | Tidy About me into groups | 9/9 | 9/9 | 136.2 | 169.0 | 21 | 27 | 602,852 | 1,096,436 |
| 21 | Category labels by what a message is | 12/12 | 11/12 | 314.0 | 277.8 | 61 | 52 | 1,279,028 | 933,457 |
| 22 | Newsletters lists decide Bulk | 10/10 | 10/10 | 143.5 | 113.8 | 25 | 18 | 758,407 | 589,757 |
| 23 | Mail meant for the user, not Bulk | 11/11 | 11/11 | 265.2 | 158.5 | 54 | 32 | 1,805,809 | 913,932 |
| 24 | Newsletter reaches the threshold | 11/11 | 11/11 | 165.0 | 209.9 | 23 | 20 | 769,567 | 666,697 |
| 25 | Learned newsletter conflicts with the user's line | 8/9 | 9/9 | 129.0 | 138.2 | 24 | 26 | 750,836 | 896,878 |
| 26 | Tabs by the rubric, over Gmail | 12/12 | 12/12 | 203.4 | 187.3 | 36 | 36 | 957,451 | 910,984 |
| 27 | User-set tab vs Gmail's re-sort | 8/8 | 8/8 | 252.0 | 169.9 | 34 | 19 | 1,290,015 | 585,136 |
| 28 | Older rubric brought up to date | 10/10 | 10/10 | 295.7 | 392.1 | 30 | 27 | 1,224,328 | 1,145,066 |
| 29 | Evidence rewrites the user's rule | 8/8 | 8/8 | 160.9 | 185.8 | 20 | 21 | 638,438 | 558,892 |
| 30 | New Gmail tab added to the table | 6/7 | 7/7 | 112.1 | 117.5 | 25 | 30 | 887,712 | 853,280 |
| 31 | Rubric overrides skill defaults | 6/6 | 6/6 | 111.5 | 104.8 | 22 | 21 | 668,859 | 574,136 |
