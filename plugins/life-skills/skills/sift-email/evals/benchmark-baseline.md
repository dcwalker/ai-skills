# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-26
**Evals**: 1-32 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 599/606 (98.8%): 296/303 run 1, 303/303 run 2 |
| Evals passing both runs | 27/32 |
| Time | 192.8s ± 74.4s |
| Tokens | 894,692 ± 357,719 (total processed, dominated by cache reads) |
| Tool calls | 28.8 ± 13.3 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial is one unattended `claude -p` turn against the Gmail, Claude Docs,
and Contacts stubs, and every eval checks that the run finishes without
waiting on the user. Graders checked labels, tabs, docs, and comments against
each stub's final state and call log, not the trial's reply.

This baseline covers replacing question comments with `(inferred)` rubric
lines (#137): when the rubric leaves a call open, sift takes the safe default
and writes the call into the rubric as a dated `(inferred)` rule in the
section for the priority it applied, and it opens and reads no comments. Both
runs were on SKILL.md as of commit 7b407a1, on 2026-10-26 in the fixtures'
rubric timezone, with fixtures anchored to 2026-10-10 and shifted two weeks.

## What the evals found

Every eval passed in at least one run, run 2 passed every check, and 27 of 32
evals passed in both.

The change held in both runs: no trial opened, read, or answered a comment;
an old answered `Sift:` comment was left alone and not applied (10); and a
collection notice the rubric leaves open became one dated `(inferred)` rule,
with no number or amount, in the section for the priority applied, recorded
in the changelog and summary (32).

Failures, all in run 1:

| Cause | Misses | Evals |
|-------|--------|-------|
| Moved the 22 Added by sift rules into Low priority word for word, without consolidating them or trimming Examples | 3 | 15 |
| The user's first-person voice in a changelog entry, copied from the rule or note it records | 2 | 28, 32 |
| Added Examples lines about threads the user's or Gmail's Important mark settled | 1 | 8 |
| Left a PTA note under the soccer heading during the About me tidy | 1 | 20 |

Eval 21's check for category labels outside `AI/` was overridden to pass in
both runs, as in earlier rounds: the only one left is the user's own seed
label "Newsletter", which sift must keep.

Not graded, seen in a few trials: eval 32's two runs disagreed on the
priority (Low priority and Junk, the second against When torn's "Low
priority over Junk"); some runs wrote `(inferred)` rules for calls the rubric
already settled; one `(inferred)` Tabs rule was a bullet below the Tabs table
rather than a row; sift's first About me note replaced the template
placeholder; and Daily review lines were duplicated or written inline.

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
- **Rubric how-to.** Seed rubrics on the current template carry the "Check
  sift's close calls" how-to line in place of "Answer a question"; the older
  rubrics in evals 15 and 28 keep their original wording.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: create docs and labels | 10/10 | 10/10 | 153.3 | 168.2 | 30 | 35 | 698,257 | 697,149 |
| 2 | Sender context; star by message | 13/13 | 13/13 | 238.1 | 294.0 | 37 | 53 | 716,394 | 1,933,307 |
| 3 | Real purchase from label history | 9/9 | 9/9 | 132.4 | 133.4 | 20 | 19 | 625,987 | 628,695 |
| 4 | Bulk, Junk, and Low priority | 9/9 | 9/9 | 162.4 | 167.1 | 29 | 28 | 791,552 | 756,252 |
| 5 | Daily review reaches the threshold | 12/12 | 12/12 | 214.9 | 173.3 | 22 | 19 | 842,680 | 551,824 |
| 6 | Daily review: nothing is a signal | 10/10 | 10/10 | 227.9 | 187.0 | 29 | 26 | 981,340 | 663,912 |
| 7 | User's edits stand on new replies | 11/11 | 11/11 | 280.8 | 275.8 | 41 | 28 | 1,694,789 | 866,393 |
| 8 | Gmail's Important mark vs the user's | 7/8 | 8/8 | 308.4 | 217.9 | 43 | 23 | 1,853,332 | 779,634 |
| 9 | New reply in a sifted thread | 8/8 | 8/8 | 169.3 | 208.9 | 24 | 22 | 763,843 | 701,920 |
| 10 | Old answered comment is ignored | 8/8 | 8/8 | 119.7 | 125.9 | 24 | 27 | 815,225 | 956,830 |
| 11 | Nothing new: cheap exit | 7/7 | 7/7 | 62.6 | 49.2 | 10 | 13 | 368,091 | 408,169 |
| 12 | Archive granted for Junk | 7/7 | 7/7 | 136.9 | 124.7 | 24 | 26 | 750,792 | 776,218 |
| 13 | Archive asked, not granted | 8/8 | 8/8 | 125.0 | 142.1 | 21 | 23 | 531,356 | 716,131 |
| 14 | Docs connector missing | 7/7 | 7/7 | 68.6 | 76.3 | 18 | 20 | 437,166 | 425,593 |
| 15 | Oversized rubric consolidation | 7/10 | 10/10 | 342.2 | 336.9 | 22 | 18 | 1,297,401 | 983,360 |
| 16 | Existing marks are context | 9/9 | 9/9 | 170.9 | 161.6 | 25 | 25 | 772,780 | 578,204 |
| 17 | About me as memory | 11/11 | 11/11 | 175.6 | 183.9 | 28 | 28 | 974,879 | 994,591 |
| 18 | Whole-inbox backlog, two pages | 11/11 | 11/11 | 336.4 | 301.9 | 86 | 79 | 1,393,870 | 1,706,361 |
| 19 | Label the rubric asks for, under AI/ | 9/9 | 9/9 | 243.5 | 188.4 | 37 | 29 | 1,149,434 | 825,223 |
| 20 | Tidy About me into groups | 8/9 | 9/9 | 151.8 | 161.6 | 22 | 21 | 792,301 | 750,292 |
| 21 | Category labels by what a message is | 13/13 | 13/13 | 325.1 | 372.7 | 51 | 58 | 1,000,311 | 1,130,806 |
| 22 | Newsletters lists decide Bulk | 10/10 | 10/10 | 129.0 | 155.0 | 18 | 21 | 557,822 | 632,703 |
| 23 | Mail meant for the user, not Bulk | 11/11 | 11/11 | 249.6 | 236.0 | 43 | 39 | 1,774,732 | 1,498,132 |
| 24 | Newsletter reaches the threshold | 11/11 | 11/11 | 148.9 | 171.7 | 19 | 20 | 504,038 | 646,183 |
| 25 | Learned newsletter conflicts with the user's line | 9/9 | 9/9 | 221.5 | 165.0 | 33 | 21 | 1,460,268 | 896,341 |
| 26 | Tabs by the rubric, over Gmail | 12/12 | 12/12 | 214.3 | 179.7 | 37 | 42 | 1,173,056 | 905,314 |
| 27 | User-set tab vs Gmail's re-sort | 8/8 | 8/8 | 255.0 | 172.7 | 29 | 20 | 792,461 | 720,302 |
| 28 | Older rubric brought up to date | 9/10 | 10/10 | 316.4 | 303.9 | 31 | 26 | 1,323,455 | 1,200,349 |
| 29 | Evidence rewrites the user's rule | 8/8 | 8/8 | 206.8 | 165.5 | 23 | 19 | 726,611 | 603,184 |
| 30 | New Gmail tab added to the table | 8/8 | 8/8 | 174.0 | 137.1 | 21 | 22 | 913,178 | 776,614 |
| 31 | Rubric overrides skill defaults | 6/6 | 6/6 | 87.0 | 85.5 | 20 | 19 | 658,935 | 659,494 |
| 32 | Close call becomes an (inferred) rule | 10/11 | 11/11 | 209.2 | 158.3 | 30 | 30 | 855,947 | 898,541 |
