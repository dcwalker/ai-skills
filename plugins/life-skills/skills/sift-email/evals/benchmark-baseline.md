# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-23
**Evals**: 1-25 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 373/380 (98.2%): 187/190 run 1, 186/190 run 2 |
| Evals passing both runs | 19/25 |
| Time | 123.5s ± 45.4s |
| Tokens | 746,906 ± 275,980 (total processed, dominated by cache reads) |
| Tool calls | 35.5 ± 15.2 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial is one unattended `claude -p` turn against the Gmail, Claude Docs,
and Contacts stubs, and every eval checks that the run finishes without
waiting on the user. Graders checked labels, docs, and comments against each
stub's final state and call log, not the trial's reply.

This baseline covers the AI/Bulk label and the rubric's Newsletters section
(PR #125). Both runs were on SKILL.md as of commit 98f73e5. Review commit
e7dfc56 then tied the newsletter label to the rubric's Category labels
section and tightened the Newsletters prose; see
[Rerun after review](#rerun-after-review).

Both runs were on 2026-10-23 in the fixtures' rubric timezone (2026-10-24 in
UTC for eval 1, whose starter rubric is UTC). The fixtures are anchored to
2026-10-10 and were not shifted. Graders held "the run date" to the date the
run's clock gave in that timezone.

## What the evals found

Every eval passed in at least one run, and 19 of 25 passed in both.

The Bulk behavior held in every graded case: newsletters on the Valued list
got Low priority, and those on Not valued or neither list got Bulk, each with
AI/Newsletter (22, and 16's school newsletter); a no-reply receipt and a
friend's FYI got Low priority, not Bulk, while a social notification and a
sale from a store the user ordered from got Bulk, not Junk (23); a subscribed
newsletter on neither list moved from Low priority to Bulk (4); and
corrections added `(learned)` lines to the right list instead of rules (24).

Failures:

| Eval | Run | Expectation missed | Cause |
|------|-----|--------------------|-------|
| 1 | 1 | Log summary carries both doc links | Linked the rubric but not the log |
| 11 | 2 | Rubric never read whole | Read the whole rubric before the Step 2 checks |
| 17 | 1 | No lookup of a covered sender | Searched contacts for a sender About me already covered |
| 18 | 1 | Lease gets Needs reply | The Oct 15 deadline had passed by the run date, as the reason said |
| 24 | 2 | New club notice gets AI/Newsletter | Treated a one-line race notice as not a newsletter |
| 25 | 2 | Question opened, and listed in the summary | Missed the label swap, which only the log shows |

The previous baseline lists the first three among behaviors seen but not
graded. Eval 18's miss comes from the run date: the previous baseline ran on
Oct 12, before the fixture's deadline. Eval 25 run 1 found the swap through
an extra search by the Bulk label.

Not graded, seen in a few trials: the Bulk and Junk split for marketing mail
varies between runs (eval 18's backlog had 33 Bulk and 0 Junk in run 1, and
22 and 11 in run 2; eval 21's one-off sale was Junk in run 1 and Bulk in run
2); log lines that leave out AI/Sifted; unrequested `(inferred)` About me
notes; and an em dash in one question comment (eval 6 run 2).

## Rerun after review

Not part of the scores. After commit e7dfc56, evals 22 and 24 were run once
more and checked by hand against their label and rubric expectations, not
graded in full. Both passed: eval 24 applied AI/Newsletter to the new club
notice, added each `(learned)` line under the right list with a changelog
entry, and added no rule under Added by sift. The rest of the suite was not
rerun on that text.

## Harness

- **Prompts.** Every eval prompt starts with `/sift-email`, followed by the
  rubric and log links (eval 1 gives none, for the first run).
- **Stubs and isolation** are unchanged from the previous baseline: Gmail,
  Claude Docs, and Contacts stubs; `run-mcp-trials.sh` turns off every plugin
  the developer has enabled, turns off auto-memory, and denies `WebFetch` in
  trials. Trial directories were under `$TMPDIR`. See evals/README.md.
- **Fixtures.** Every rubric fixture follows the current template, and every
  Gmail fixture with AI labels carries AI/Bulk as Label_27.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: create docs and labels | 8/9 | 9/9 | 120.3 | 158.4 | 34 | 31 | 738,286 | 771,606 |
| 2 | Sender context; Needs reply by message | 11/11 | 11/11 | 189.7 | 178.9 | 48 | 43 | 1,084,334 | 1,048,496 |
| 3 | Real purchase from label history | 7/7 | 7/7 | 67.3 | 80.3 | 27 | 28 | 456,233 | 552,575 |
| 4 | Bulk, Junk, and Low priority | 7/7 | 7/7 | 97.7 | 107.9 | 40 | 39 | 662,808 | 669,827 |
| 5 | AI/Wrong with a clear direction | 9/9 | 9/9 | 132.4 | 135.0 | 33 | 32 | 765,310 | 634,489 |
| 6 | AI/Wrong unclear: question, no block | 8/8 | 8/8 | 131.9 | 150.8 | 26 | 35 | 885,263 | 886,042 |
| 7 | Swapped and added labels | 6/6 | 6/6 | 176.6 | 161.4 | 30 | 30 | 613,186 | 533,390 |
| 8 | Removed label | 5/5 | 5/5 | 119.7 | 118.3 | 27 | 25 | 623,351 | 439,734 |
| 9 | New reply in a sifted thread | 6/6 | 6/6 | 76.2 | 85.8 | 28 | 31 | 619,161 | 737,372 |
| 10 | Answered question applied | 7/7 | 7/7 | 85.8 | 125.5 | 27 | 25 | 612,369 | 418,135 |
| 11 | Nothing new: cheap exit | 6/6 | 5/6 | 38.3 | 43.4 | 20 | 22 | 350,159 | 404,412 |
| 12 | Archive granted for Junk | 4/4 | 4/4 | 92.1 | 98.5 | 31 | 36 | 591,014 | 728,346 |
| 13 | Archive asked, not granted | 6/6 | 6/6 | 92.0 | 89.7 | 23 | 34 | 612,463 | 529,398 |
| 14 | Docs connector missing | 7/7 | 7/7 | 63.3 | 64.7 | 19 | 21 | 487,863 | 551,105 |
| 15 | Oversized rubric consolidation | 9/9 | 9/9 | 129.6 | 180.9 | 25 | 33 | 661,321 | 1,000,534 |
| 16 | Existing labels are context | 7/7 | 7/7 | 123.9 | 97.7 | 44 | 37 | 881,111 | 740,895 |
| 17 | About me as memory | 8/9 | 9/9 | 112.7 | 133.2 | 32 | 45 | 608,358 | 936,235 |
| 18 | Whole-inbox backlog, two pages | 7/8 | 8/8 | 239.4 | 208.0 | 97 | 95 | 1,641,872 | 1,299,025 |
| 19 | Label the rubric asks for, under AI/ | 6/6 | 6/6 | 129.3 | 135.8 | 43 | 35 | 706,374 | 665,796 |
| 20 | Tidy About me into groups | 8/8 | 8/8 | 109.9 | 96.7 | 29 | 27 | 683,263 | 669,384 |
| 21 | Category labels by what a message is | 10/10 | 10/10 | 195.6 | 205.0 | 57 | 62 | 666,358 | 957,531 |
| 22 | Newsletters lists decide Bulk | 9/9 | 9/9 | 83.8 | 68.2 | 34 | 28 | 752,479 | 597,547 |
| 23 | Mail meant for the user, not Bulk | 9/9 | 9/9 | 150.4 | 193.5 | 45 | 48 | 1,205,862 | 1,758,790 |
| 24 | Newsletter corrections as learned lines | 10/10 | 9/10 | 159.7 | 159.1 | 30 | 29 | 664,291 | 692,712 |
| 25 | Correction conflicts with a user's line | 7/7 | 5/7 | 109.0 | 72.0 | 29 | 26 | 919,843 | 628,971 |
