# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-24
**Evals**: 1-25 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 389/392 (99.2%): 194/196 run 1, 195/196 run 2 |
| Evals passing both runs | 22/25 |
| Time | 129.3s ± 53.0s |
| Tokens | 737,670 ± 278,065 (total processed, dominated by cache reads) |
| Tool calls | 27.3 ± 15.0 |

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
on SKILL.md as of commit 8783315.

Both runs were on 2026-10-24 in the fixtures' rubric timezone (2026-10-25 in
UTC for eval 1, whose starter rubric is UTC). The fixtures are anchored to
2026-10-10 and were shifted two weeks. Graders held "the run date" to the
date the run's clock gave in that timezone.

## What the evals found

Every eval passed in at least one run, and 22 of 25 passed in both.

The new behavior held in every graded case but two. The daily review added
an `(observed)` rule only at the third agreeing signal, and none for a sender
with two (5); found no signal in mail read and archived, a receipt left
unread, a priority the user changed, or a reply to a thread sift starred
(6); and added a newsletter to Valued (24), or opened a question when the
signals conflicted with the user's Not valued line (25). A thread the user
swapped from Important to Low priority stayed Low priority on a new reply
(7). Gmail's own Important mark came off a sale sift called Junk (16) and off
a group thread whose new message Gmail had marked (8), while a mark the user
had set on an earlier message stayed (8). Stars were never removed.

Failures:

| Eval | Run | Expectation missed | Cause |
|------|-----|--------------------|-------|
| 5 | 1 | `(observed)` rule names the sender and Low priority | The rule named the sender but not the priority it applies; the changelog and log named it |
| 7 | 1 | No star added to `t-unstarred` | Starred the landlord's thread again after the user removed sift's star, because the new message asked something |
| 11 | 2 | Rubric never read whole | Read the whole rubric before the Step 2 checks, as in the previous baseline |

Not graded, seen in a few trials: eval 11 run 1 rewrote the empty run's
heading as a plain paragraph, which the next run reads its search start
from; eval 13 run 2 stored an account's last four digits in an `(inferred)`
About me note; eval 2 run 1 marked a "Got it, thanks!" reply Important under
the 90-day rule though its own searches found no mail to that sender; the
Bulk and Junk split for marketing mail varies between runs (eval 1's promo,
eval 21's sale); run headings sometimes land at the wrong level or above the
Runs intro; the Daily review note usually sits in the run summary rather
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
| 1 | First run: create docs and labels | 9/9 | 9/9 | 139.6 | 141.2 | 30 | 30 | 795,979 | 814,273 |
| 2 | Sender context; star by message | 11/11 | 11/11 | 201.9 | 187.6 | 45 | 44 | 1,222,158 | 1,316,787 |
| 3 | Real purchase from label history | 7/7 | 7/7 | 85.8 | 73.4 | 19 | 22 | 639,335 | 647,724 |
| 4 | Bulk, Junk, and Low priority | 7/7 | 7/7 | 99.0 | 119.1 | 26 | 27 | 646,746 | 634,377 |
| 5 | Daily review reaches the threshold | 9/10 | 10/10 | 121.4 | 162.8 | 23 | 23 | 726,714 | 756,468 |
| 6 | Daily review: nothing is a signal | 8/8 | 8/8 | 193.5 | 146.3 | 26 | 29 | 539,352 | 764,319 |
| 7 | User's edits stand on new replies | 8/9 | 9/9 | 220.7 | 178.6 | 23 | 21 | 632,642 | 598,822 |
| 8 | Gmail's Important mark vs the user's | 7/7 | 7/7 | 114.5 | 145.1 | 18 | 17 | 625,113 | 524,604 |
| 9 | New reply in a sifted thread | 6/6 | 6/6 | 123.8 | 85.0 | 23 | 20 | 800,167 | 456,233 |
| 10 | Answered question applied | 7/7 | 7/7 | 124.1 | 138.8 | 20 | 21 | 709,531 | 670,419 |
| 11 | Nothing new: cheap exit | 6/6 | 5/6 | 33.0 | 31.9 | 11 | 12 | 329,483 | 317,443 |
| 12 | Archive granted for Junk | 4/4 | 4/4 | 72.1 | 92.9 | 25 | 27 | 610,079 | 883,356 |
| 13 | Archive asked, not granted | 6/6 | 6/6 | 87.9 | 106.0 | 22 | 23 | 653,285 | 603,403 |
| 14 | Docs connector missing | 7/7 | 7/7 | 41.6 | 34.5 | 12 | 11 | 294,838 | 277,314 |
| 15 | Oversized rubric consolidation | 9/9 | 9/9 | 128.9 | 189.7 | 15 | 18 | 547,518 | 765,930 |
| 16 | Existing marks are context | 7/7 | 7/7 | 97.1 | 114.4 | 24 | 29 | 611,572 | 686,890 |
| 17 | About me as memory | 9/9 | 9/9 | 138.3 | 118.6 | 26 | 27 | 849,482 | 812,626 |
| 18 | Whole-inbox backlog, two pages | 8/8 | 8/8 | 292.2 | 200.7 | 89 | 83 | 1,743,971 | 1,163,894 |
| 19 | Label the rubric asks for, under AI/ | 6/6 | 6/6 | 128.9 | 146.0 | 31 | 32 | 708,830 | 843,077 |
| 20 | Tidy About me into groups | 8/8 | 8/8 | 118.0 | 110.3 | 22 | 24 | 743,236 | 839,850 |
| 21 | Category labels by what a message is | 10/10 | 10/10 | 220.2 | 232.0 | 57 | 47 | 782,649 | 951,225 |
| 22 | Newsletters lists decide Bulk | 9/9 | 9/9 | 98.2 | 88.5 | 24 | 17 | 719,084 | 443,318 |
| 23 | Mail meant for the user, not Bulk | 9/9 | 9/9 | 188.9 | 103.6 | 42 | 26 | 1,601,452 | 671,654 |
| 24 | Newsletter reaches the threshold | 9/9 | 9/9 | 116.2 | 113.9 | 18 | 22 | 567,583 | 739,956 |
| 25 | Learned newsletter conflicts with the user's line | 8/8 | 8/8 | 105.1 | 110.9 | 21 | 23 | 741,001 | 857,738 |
