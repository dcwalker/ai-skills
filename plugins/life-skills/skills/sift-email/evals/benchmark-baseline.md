# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-24
**Evals**: 1-25 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 410/412 (99.5%): 205/206 run 1, 205/206 run 2 |
| Evals passing both runs | 24/25 |
| Time | 133.7s ± 57.2s |
| Tokens | 748,760 ± 307,696 (total processed, dominated by cache reads) |
| Tool calls | 28.0 ± 15.7 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial is one unattended `claude -p` turn against the Gmail, Claude Docs,
and Contacts stubs, and every eval checks that the run finishes without
waiting on the user. Graders checked labels, docs, and comments against each
stub's final state and call log, not the trial's reply.

This baseline covers Gmail's Important mark and star in place of
`AI/Important`, `AI/Needs reply`, `AI/Sifted`, and `AI/Wrong`; the search
for new mail by the last run's epoch seconds; the user's own edits standing;
and the daily review of how the user handled mail (PR #129). Both runs were
on SKILL.md as of commit 4d9f1c0.

Both runs were on 2026-10-24 in the fixtures' rubric timezone (2026-10-25 in
UTC for eval 1, whose starter rubric is UTC). The fixtures are anchored to
2026-10-10 and were shifted two weeks. Graders held "the run date" to the
date the run's clock gave in that timezone.

## What the evals found

Every eval passed in at least one run, and 24 of 25 passed in both.

The new behavior held in every graded case. The daily review added an
`(observed)` rule naming the sender and its priority only at the third
agreeing signal, and none for a sender with two (5); found no signal in mail
read and archived, a receipt left unread, a priority the user changed, or a
reply to a thread sift starred (6); and added a newsletter to Valued (24), or
opened a question when the signals conflicted with the user's Not valued line
(25). A thread the user swapped from Important to Low priority stayed Low
priority on a new reply, a star the user removed came back when a new message
asked something, and stayed off when the new message only said thanks (7).
Gmail's own Important mark came off a sale sift called Junk (16) and off a
group thread whose new message Gmail had marked (8), while a mark the user had
set on an earlier message stayed (8). No run edited a run heading when it had
nothing new (11), and no rubric line held account digits.

Failures:

| Eval | Run | Expectation missed | Cause |
|------|-----|--------------------|-------|
| 11 | 1 | Rubric never read whole | Read the whole rubric before the Step 2 checks |
| 11 | 2 | Rubric never read whole | Same; the previous two baselines missed this in one run each |

Not graded, seen in a few trials: eval 18 run 1 wrote its run heading in
bold rather than as a `###` heading, which the next run reads its search
start from; run entries sometimes land above the Runs intro (evals 1 and 24);
eval 3 run 1 wrote an `(inferred)` note in first person; the Bulk and Junk
split for marketing and list mail varies between runs (eval 19's potluck
invitation); the Daily review note usually sits in the run summary rather
than on its own line; and unrequested `(inferred)` About me notes and
category labels.

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
  in evals 18 and 19 are date tokens.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: create docs and labels | 9/9 | 9/9 | 136.9 | 204.7 | 34 | 39 | 893,844 | 1,426,598 |
| 2 | Sender context; star by message | 11/11 | 11/11 | 173.0 | 190.5 | 34 | 42 | 794,611 | 1,165,586 |
| 3 | Real purchase from label history | 7/7 | 7/7 | 75.7 | 99.7 | 21 | 17 | 624,748 | 485,995 |
| 4 | Bulk, Junk, and Low priority | 8/8 | 8/8 | 119.2 | 105.5 | 27 | 28 | 694,864 | 635,880 |
| 5 | Daily review reaches the threshold | 10/10 | 10/10 | 141.7 | 144.0 | 21 | 22 | 667,543 | 750,231 |
| 6 | Daily review: nothing is a signal | 9/9 | 9/9 | 171.0 | 140.1 | 29 | 27 | 794,829 | 669,760 |
| 7 | User's edits stand on new replies | 10/10 | 10/10 | 200.8 | 259.7 | 24 | 41 | 786,714 | 1,725,011 |
| 8 | Gmail's Important mark vs the user's | 7/7 | 7/7 | 168.9 | 165.2 | 29 | 24 | 826,906 | 719,500 |
| 9 | New reply in a sifted thread | 6/6 | 6/6 | 101.8 | 88.4 | 21 | 23 | 669,509 | 650,390 |
| 10 | Answered question applied | 7/7 | 7/7 | 123.1 | 93.2 | 21 | 16 | 735,259 | 396,171 |
| 11 | Nothing new: cheap exit | 6/7 | 6/7 | 51.5 | 74.0 | 11 | 14 | 295,565 | 430,333 |
| 12 | Archive granted for Junk | 5/5 | 5/5 | 74.6 | 83.7 | 22 | 23 | 499,083 | 611,997 |
| 13 | Archive asked, not granted | 7/7 | 7/7 | 81.9 | 78.0 | 21 | 21 | 503,809 | 600,126 |
| 14 | Docs connector missing | 7/7 | 7/7 | 56.3 | 39.4 | 16 | 11 | 455,738 | 379,773 |
| 15 | Oversized rubric consolidation | 9/9 | 9/9 | 140.2 | 118.6 | 16 | 14 | 643,190 | 432,494 |
| 16 | Existing marks are context | 7/7 | 7/7 | 103.1 | 112.2 | 27 | 27 | 638,253 | 703,589 |
| 17 | About me as memory | 9/9 | 9/9 | 128.0 | 113.8 | 20 | 22 | 616,098 | 670,782 |
| 18 | Whole-inbox backlog, two pages | 9/9 | 9/9 | 240.0 | 266.8 | 88 | 94 | 1,112,051 | 1,413,501 |
| 19 | Label the rubric asks for, under AI/ | 7/7 | 7/7 | 158.9 | 112.5 | 33 | 30 | 656,403 | 678,921 |
| 20 | Tidy About me into groups | 8/8 | 8/8 | 110.5 | 144.7 | 19 | 22 | 646,538 | 797,054 |
| 21 | Category labels by what a message is | 11/11 | 11/11 | 318.6 | 193.5 | 54 | 48 | 1,193,856 | 743,401 |
| 22 | Newsletters lists decide Bulk | 9/9 | 9/9 | 80.2 | 85.6 | 21 | 19 | 512,899 | 415,871 |
| 23 | Mail meant for the user, not Bulk | 9/9 | 9/9 | 197.9 | 149.8 | 44 | 32 | 1,652,293 | 965,995 |
| 24 | Newsletter reaches the threshold | 9/9 | 9/9 | 126.6 | 99.0 | 25 | 17 | 866,170 | 466,384 |
| 25 | Learned newsletter conflicts with the user's line | 9/9 | 9/9 | 136.5 | 107.8 | 27 | 21 | 1,051,485 | 670,422 |
