# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-27
**Evals**: 1-37 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 669/682 (98.1%): 334/341 run 1, 335/341 run 2 |
| Evals passing both runs | 28/37 |
| Time | 221.3s ± 93.7s |
| Tokens | 1,263,816 ± 418,044 (total processed, dominated by cache reads) |
| Tool calls | 34.6 ± 15.1 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial runs against the Gmail and Contacts stubs and a fake GitHub
(`evals/lib/github-fixture.py`). Graders checked labels, commits, and files
against each stub's final state and call log, not the trial's reply.

This baseline covers moving sift's labels out of the `AI/` parent to plain
top-level names, so the user can show or hide each one in Gmail. The
priority labels are `Low priority`, `Bulk`, and `Junk`. The rubric's Labels
table now lists every label in the account, the user's own included: sift
applies any label whose row fits, unless the row says sift doesn't apply it,
and adds an "(inferred)" row for each user label that lacks one, from that
label's recent threads. A label the rubric asks for is created in title case
unless one of that name already exists, in any case. Both runs were on the
SKILL.md in this branch, on 2026-10-27, with fixtures anchored to 2026-10-10
and shifted to the run date.

Evals 6, 11, and 37 were rerun on 2026-10-27 after a run with no new mail
but a due daily review was changed to still tidy the rubric and commit,
rather than stop with "Nothing new". Their rows below are from that rerun.

## What the evals found

28 of 37 evals passed in both runs; eval 16 missed a different check in each
run, and every other eval passed in at least one.

The label change held in every trial: no trial created a label under `AI/`,
a duplicate of one of the user's labels, or a case variant of one. With an
uncataloged Soccer label, sift added an inferred row from its threads and
applied it to the new coach's message, not to the school's (35); with a
lowercase `travel` label, it used that label rather than creating `Travel`
(36); the newsletter label it learns is the user's own Newsletter (21, 24,
26). With no new mail but the daily review due, sift still tidied the
rubric, adding the Soccer row, set the `Daily review:` line, and committed
both files in one commit, changing no labels (37); with the review already
done, it still stopped with "Nothing new" and no commit (11).

Failures:

| Cause | Misses | Evals |
|-------|--------|-------|
| Said t-kudos moved to Social in the commit, state, and reply when it stayed in Updates, and wrote a changelog line in the first person (run 1) | 3 | 26 |
| Moved the Added by sift rules into Low priority without consolidating them or trimming Examples (run 2) | 2 | 15 |
| An order number in the commit message (16 run 1, 23 run 2) | 2 | 16, 23 |
| Labeled Gmail's important marketing Bulk, not Junk (run 2) | 1 | 16 |
| A changelog line in the first person (run 2) | 1 | 19 |
| Quoted a rubric rule in the first person in the reply (run 2) | 1 | 6 |
| Started the inferred Soccer row with "(inferred, <date>)" (run 1) | 1 | 37 |
| Added a rule and example about a thread the user had relabeled (run 1) | 1 | 7 |
| Rewrapped the Permissions paragraph, so it differs from the seed in line breaks only (run 1) | 1 | 28 |

Not graded, seen in a few trials: sift created category labels that have a
row in the template's Labels table without being asked (Delivery,
Statement), and in eval 30 created `Receipt` beside the user's `Receipts`,
since the names differ; some trials read the harness's own files in the run
directory, and one ran `env`, printing the stubs' proxy credentials into its
transcript; a few commit bodies miscounted priorities; and one run's commit
had no co-author line.

## Harness

- **Prompts.** Every eval prompt is `/sift-email`. Evals 10 and 14 add that
  the run was started by a schedule, with no one to answer; eval 13 adds the
  request to archive junk. Eval 1 has a follow-up turn naming the repository.
- **Fixtures.** Each Gmail state drops the `AI` parent and renames `AI/X` to
  `X`; in fixtures 24 and 25 the learned newsletter label is merged into the
  user's own Newsletter. Each rubric's Labels table gains a row for each of
  the user's labels. Evals 35 and 36 are new, built on fixture 5; eval 37
  is new, built on fixture 11 with fixture 35's rubric and Soccer threads.
- **Stubs and isolation** are unchanged from the previous baseline.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: ask, then create files and labels | 11/11 | 11/11 | 245.3 | 289.6 | 51 | 64 | 1,815,485 | 2,308,701 |
| 2 | Sender context; star by message | 13/13 | 13/13 | 349.2 | 234.7 | 44 | 49 | 1,526,597 | 1,521,953 |
| 3 | Real purchase from label history | 9/9 | 9/9 | 147.0 | 159.1 | 26 | 35 | 1,066,110 | 1,254,687 |
| 4 | Bulk, Junk, and Low priority | 9/9 | 9/9 | 209.8 | 179.5 | 27 | 36 | 995,922 | 1,110,902 |
| 5 | Daily review reaches the threshold | 11/11 | 11/11 | 221.2 | 241.1 | 32 | 33 | 1,325,092 | 1,082,596 |
| 6 | Daily review: nothing is a signal | 9/9 | 8/9 | 291.8 | 267.5 | 42 | 33 | 1,611,058 | 1,069,674 |
| 7 | User's edits stand on new replies | 9/10 | 10/10 | 290.4 | 259.8 | 38 | 42 | 1,542,623 | 1,363,039 |
| 8 | Gmail's Important mark vs the user's | 8/8 | 8/8 | 285.6 | 194.2 | 36 | 36 | 1,403,742 | 1,228,856 |
| 9 | New reply in a sifted thread | 8/8 | 8/8 | 192.8 | 187.4 | 28 | 34 | 1,020,265 | 1,355,284 |
| 10 | Another user's checkout is skipped | 9/9 | 9/9 | 93.3 | 122.6 | 17 | 25 | 568,440 | 813,414 |
| 11 | Nothing new: cheap exit | 5/5 | 5/5 | 43.0 | 42.9 | 13 | 13 | 476,132 | 476,261 |
| 12 | Archive granted for Junk | 7/7 | 7/7 | 152.6 | 151.8 | 28 | 31 | 1,112,959 | 1,264,910 |
| 13 | Archive asked, not granted | 8/8 | 8/8 | 176.6 | 155.6 | 29 | 30 | 1,240,675 | 1,028,323 |
| 14 | gh not logged in | 8/8 | 8/8 | 138.7 | 96.2 | 23 | 17 | 808,141 | 568,784 |
| 15 | Oversized rubric consolidation | 10/10 | 8/10 | 297.9 | 249.4 | 30 | 27 | 1,584,881 | 1,275,903 |
| 16 | Existing marks are context | 8/9 | 8/9 | 147.1 | 219.7 | 29 | 35 | 993,800 | 1,243,479 |
| 17 | About me as memory | 11/11 | 11/11 | 147.4 | 146.5 | 29 | 29 | 921,852 | 934,330 |
| 18 | Whole-inbox backlog, two pages | 11/11 | 11/11 | 369.9 | 479.5 | 83 | 106 | 1,672,144 | 2,722,512 |
| 19 | Label the rubric asks for | 9/9 | 8/9 | 179.1 | 196.9 | 38 | 34 | 1,081,234 | 1,099,291 |
| 20 | Tidy About me into groups | 9/9 | 9/9 | 318.8 | 303.1 | 30 | 24 | 1,484,565 | 1,212,687 |
| 21 | Category labels by what a message is | 13/13 | 13/13 | 301.2 | 358.2 | 60 | 70 | 1,059,239 | 1,755,674 |
| 22 | Newsletters lists decide Bulk | 10/10 | 10/10 | 122.4 | 170.7 | 21 | 26 | 773,963 | 939,114 |
| 23 | Mail meant for the user, not Bulk | 11/11 | 10/11 | 252.9 | 202.2 | 50 | 46 | 1,563,972 | 1,546,378 |
| 24 | Newsletter reaches the threshold | 10/10 | 10/10 | 375.2 | 195.1 | 37 | 24 | 1,652,747 | 1,000,591 |
| 25 | Learned newsletter conflicts with the user's line | 8/8 | 8/8 | 199.9 | 311.4 | 32 | 33 | 1,375,142 | 1,602,095 |
| 26 | Tabs by the rubric, over Gmail | 9/12 | 12/12 | 383.0 | 205.4 | 58 | 43 | 1,706,635 | 1,332,621 |
| 27 | User-set tab vs Gmail's re-sort | 8/8 | 8/8 | 397.7 | 295.6 | 41 | 36 | 1,468,097 | 1,398,791 |
| 28 | Older rubric brought up to date | 9/10 | 10/10 | 376.4 | 355.7 | 33 | 31 | 1,733,677 | 1,375,648 |
| 29 | Evidence rewrites the user's rule | 7/7 | 7/7 | 277.9 | 224.3 | 34 | 26 | 1,818,263 | 1,006,065 |
| 30 | New Gmail tab added to the table | 8/8 | 8/8 | 166.7 | 187.7 | 30 | 33 | 1,424,290 | 1,426,607 |
| 31 | Rubric overrides skill defaults | 5/5 | 5/5 | 129.3 | 101.4 | 21 | 18 | 869,585 | 767,442 |
| 32 | Close call becomes an (inferred) rule | 10/10 | 10/10 | 367.0 | 210.7 | 42 | 37 | 2,033,146 | 1,402,488 |
| 33 | Search finds only the user's private repo | 10/10 | 10/10 | 268.5 | 174.6 | 35 | 31 | 1,615,209 | 1,331,115 |
| 34 | No usable rubric: ask before writing | 7/7 | 7/7 | 56.7 | 41.8 | 11 | 7 | 398,826 | 235,589 |
| 35 | User label cataloged and applied | 11/11 | 11/11 | 375.5 | 209.4 | 35 | 34 | 1,643,354 | 1,402,118 |
| 36 | Existing label used, any case | 9/9 | 9/9 | 179.1 | 154.6 | 32 | 29 | 1,420,791 | 879,798 |
| 37 | Daily review due, no new mail: tidy and commit | 7/8 | 8/8 | 154.3 | 120.0 | 31 | 25 | 1,311,679 | 1,064,367 |
