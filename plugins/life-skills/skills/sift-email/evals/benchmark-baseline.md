# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-25
**Evals**: 1-25 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 419/422 (99.3%): 209/211 run 1, 210/211 run 2 |
| Evals passing both runs | 22/25 |
| Time | 148.1s ± 59.7s |
| Tokens | 848,190 ± 362,123 (total processed, dominated by cache reads) |
| Tool calls | 30.2 ± 16.2 |

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
on SKILL.md as of commit ed3df62.

Eval 11 in both runs comes from a rerun on that same SKILL.md. The first pair
ran just after midnight in the rubric's timezone, so the fixture's "daily
review already ran" entry, dated by the shifted fixture, was a day old: the
review was due, and the eval never reached its cheap exit. The fixture now
dates that entry by the trial's own clock (`{{today:America/Chicago}}`).

Runs were on 2026-10-25 in the fixtures' rubric timezone. The fixtures are
anchored to 2026-10-10 and were shifted two weeks. Graders held "the run
date" to the date the run's clock gave in that timezone.

## What the evals found

Every eval passed in at least one run, and 22 of 25 passed in both.

The new behavior held. The daily review added an `(observed)` rule naming
the sender and its priority only at the third agreeing signal, and none for a
sender with two (5); found no signal in mail read and archived, a receipt
left unread, a priority the user changed, or a reply to a thread sift starred
(6); and added a newsletter to Valued (24), or opened a question when the
signals conflicted with the user's Not valued line (25). A thread the user
swapped from Important to Low priority stayed Low priority on a new reply, a
star the user removed came back when a new message asked something, and
stayed off when the new message only said thanks (7). Gmail's own Important
mark came off a sale sift called Junk (16) and off a group thread whose new
message Gmail had marked (8), while a mark the user had set stayed (8). Every
run heading was a `###` heading after the Runs intro (2, 5, 9, 18, 24), no
run with nothing new read the rubric whole or edited a heading (11), and no
rubric line held account digits.

Failures:

| Eval | Run | Expectation missed | Cause |
|------|-----|--------------------|-------|
| 7 | 1 | Changelog unchanged | Logged its own new `(inferred)` About me notes in the changelog; no rule was learned from the user's edits |
| 8 | 1 | No call removes IMPORTANT from the user's thread | Removed the mark before fetching the thread, then restored it; the end state is right |
| 23 | 2 | Unsolicited sale is Junk | Read the list's "you subscribed" footer as a relationship and chose Bulk |

Not graded, seen in a few trials: the Bulk and Junk split for marketing and
list mail varies between runs (eval 21's sale, eval 19's potluck);
`(inferred)` About me notes sometimes replace the template's placeholder
topic; the Daily review note usually sits in the run summary rather than on
its own line; log summaries sometimes miscount; and unrequested category
labels.

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
| 1 | First run: create docs and labels | 9/9 | 9/9 | 135.1 | 122.1 | 30 | 29 | 722,096 | 730,868 |
| 2 | Sender context; star by message | 12/12 | 12/12 | 227.4 | 247.8 | 43 | 53 | 1,177,753 | 1,764,708 |
| 3 | Real purchase from label history | 7/7 | 7/7 | 120.7 | 88.7 | 17 | 22 | 583,123 | 602,849 |
| 4 | Bulk, Junk, and Low priority | 8/8 | 8/8 | 111.0 | 133.2 | 26 | 31 | 611,046 | 792,782 |
| 5 | Daily review reaches the threshold | 11/11 | 11/11 | 190.8 | 187.0 | 28 | 33 | 1,031,905 | 1,372,396 |
| 6 | Daily review: nothing is a signal | 9/9 | 9/9 | 211.4 | 146.1 | 29 | 28 | 820,061 | 782,783 |
| 7 | User's edits stand on new replies | 9/10 | 10/10 | 264.6 | 218.5 | 48 | 29 | 1,984,764 | 803,962 |
| 8 | Gmail's Important mark vs the user's | 6/7 | 7/7 | 213.9 | 191.9 | 27 | 27 | 1,028,214 | 843,859 |
| 9 | New reply in a sifted thread | 7/7 | 7/7 | 105.6 | 109.0 | 25 | 22 | 705,520 | 648,006 |
| 10 | Answered question applied | 7/7 | 7/7 | 153.6 | 115.7 | 25 | 19 | 989,763 | 539,308 |
| 11 | Nothing new: cheap exit | 7/7 | 7/7 | 51.2 | 52.5 | 15 | 12 | 447,762 | 341,919 |
| 12 | Archive granted for Junk | 5/5 | 5/5 | 96.2 | 84.1 | 26 | 26 | 653,078 | 566,249 |
| 13 | Archive asked, not granted | 7/7 | 7/7 | 93.0 | 99.2 | 20 | 25 | 543,656 | 586,875 |
| 14 | Docs connector missing | 7/7 | 7/7 | 59.4 | 54.7 | 17 | 15 | 479,137 | 399,829 |
| 15 | Oversized rubric consolidation | 9/9 | 9/9 | 134.4 | 139.0 | 17 | 16 | 533,263 | 658,832 |
| 16 | Existing marks are context | 7/7 | 7/7 | 125.8 | 129.2 | 28 | 34 | 722,145 | 776,840 |
| 17 | About me as memory | 9/9 | 9/9 | 134.9 | 117.2 | 27 | 25 | 818,908 | 741,727 |
| 18 | Whole-inbox backlog, two pages | 10/10 | 10/10 | 284.2 | 228.6 | 95 | 93 | 1,835,092 | 1,324,095 |
| 19 | Label the rubric asks for, under AI/ | 7/7 | 7/7 | 171.2 | 147.9 | 34 | 29 | 807,502 | 817,955 |
| 20 | Tidy About me into groups | 8/8 | 8/8 | 127.1 | 199.1 | 21 | 28 | 770,493 | 1,264,032 |
| 21 | Category labels by what a message is | 11/11 | 11/11 | 298.4 | 214.4 | 57 | 50 | 1,256,943 | 766,295 |
| 22 | Newsletters lists decide Bulk | 9/9 | 9/9 | 134.4 | 86.5 | 26 | 18 | 1,035,094 | 574,403 |
| 23 | Mail meant for the user, not Bulk | 9/9 | 8/9 | 219.5 | 156.8 | 43 | 33 | 1,559,263 | 749,477 |
| 24 | Newsletter reaches the threshold | 10/10 | 10/10 | 105.2 | 121.5 | 19 | 20 | 465,390 | 678,736 |
| 25 | Learned newsletter conflicts with the user's line | 9/9 | 9/9 | 137.2 | 110.1 | 27 | 22 | 938,758 | 759,980 |
