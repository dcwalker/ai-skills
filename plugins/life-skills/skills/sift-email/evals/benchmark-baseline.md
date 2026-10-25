# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-25
**Evals**: 1-25 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 422/422 (100.0%): 211/211 run 1, 211/211 run 2 |
| Evals passing both runs | 25/25 |
| Time | 139.7s ± 54.4s |
| Tokens | 780,215 ± 326,886 (total processed, dominated by cache reads) |
| Tool calls | 29.5 ± 15.2 |

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
on SKILL.md as of commit 323be7f.

Runs were on 2026-10-25 in the fixtures' rubric timezone. The fixtures are
anchored to 2026-10-10 and were shifted two weeks; eval 11's "daily review
already ran" entry follows the trial's own clock. Graders held "the run date"
to the date the run's clock gave in that timezone.

## What the evals found

Every expectation passed in both runs.

The daily review added an `(observed)` rule naming the sender and its
priority only at the third agreeing signal, and none for a sender with two
(5); found no signal in mail read and archived, a receipt left unread, a
priority the user changed, or a reply to a thread sift starred (6); and added
a newsletter to Valued (24), or opened a question when the signals conflicted
with the user's Not valued line (25). A thread the user swapped from
Important to Low priority stayed Low priority on a new reply, a star the user
removed came back when a new message asked something, and stayed off when the
new message only said thanks (7). Every thread with a new reply was fetched
before any label change, so Gmail's own Important mark came off a group
thread while a mark the user had set stayed, with no call removing it (8).
Every run heading was a `###` heading after the Runs intro (2, 5, 9, 18, 24),
no run with nothing new read the rubric whole or edited a heading (11), and
no rubric line held account digits.

Not graded, seen in a few trials: the Bulk and Junk split for marketing and
list mail varies between runs (evals 2, 14, and 19); category labels the
eval's rubric doesn't name are sometimes created (`AI/Newsletter`,
`AI/Delivery`, `AI/Appointment`); a changelog entry for sift's own
`(inferred)` notes appears in some runs and not others; one run heading in
eval 1, which has no heading check, landed above the Runs intro; the Daily
review note usually sits in the run summary rather than on its own line; and
log formatting varies (bullets, bold, em dashes).

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
| 1 | First run: create docs and labels | 9/9 | 9/9 | 96.7 | 123.5 | 28 | 28 | 628,655 | 728,096 |
| 2 | Sender context; star by message | 12/12 | 12/12 | 258.8 | 230.8 | 52 | 54 | 2,026,705 | 1,592,171 |
| 3 | Real purchase from label history | 7/7 | 7/7 | 74.1 | 99.4 | 18 | 20 | 472,318 | 564,605 |
| 4 | Bulk, Junk, and Low priority | 8/8 | 8/8 | 103.3 | 106.2 | 28 | 31 | 727,872 | 509,188 |
| 5 | Daily review reaches the threshold | 11/11 | 11/11 | 142.9 | 170.4 | 27 | 28 | 867,095 | 934,945 |
| 6 | Daily review: nothing is a signal | 9/9 | 9/9 | 165.6 | 155.5 | 31 | 26 | 1,021,632 | 854,019 |
| 7 | User's edits stand on new replies | 10/10 | 10/10 | 164.0 | 227.9 | 28 | 32 | 694,357 | 962,145 |
| 8 | Gmail's Important mark vs the user's | 7/7 | 7/7 | 219.1 | 150.7 | 31 | 27 | 907,392 | 835,420 |
| 9 | New reply in a sifted thread | 7/7 | 7/7 | 106.5 | 112.9 | 22 | 22 | 601,757 | 682,689 |
| 10 | Answered question applied | 7/7 | 7/7 | 104.5 | 148.9 | 18 | 20 | 491,767 | 439,862 |
| 11 | Nothing new: cheap exit | 7/7 | 7/7 | 53.1 | 43.6 | 14 | 11 | 396,499 | 305,866 |
| 12 | Archive granted for Junk | 5/5 | 5/5 | 97.8 | 97.5 | 26 | 27 | 716,506 | 580,251 |
| 13 | Archive asked, not granted | 7/7 | 7/7 | 113.2 | 128.2 | 21 | 25 | 652,655 | 698,531 |
| 14 | Docs connector missing | 7/7 | 7/7 | 81.2 | 59.8 | 20 | 17 | 517,063 | 422,087 |
| 15 | Oversized rubric consolidation | 9/9 | 9/9 | 193.3 | 149.8 | 19 | 23 | 709,672 | 898,219 |
| 16 | Existing marks are context | 7/7 | 7/7 | 114.6 | 109.2 | 24 | 27 | 596,581 | 661,677 |
| 17 | About me as memory | 9/9 | 9/9 | 131.0 | 111.2 | 28 | 27 | 805,223 | 804,727 |
| 18 | Whole-inbox backlog, two pages | 10/10 | 10/10 | 231.3 | 245.0 | 82 | 95 | 1,000,271 | 1,190,489 |
| 19 | Label the rubric asks for, under AI/ | 7/7 | 7/7 | 150.4 | 122.7 | 32 | 27 | 712,331 | 607,207 |
| 20 | Tidy About me into groups | 8/8 | 8/8 | 142.4 | 144.1 | 23 | 29 | 821,717 | 1,095,493 |
| 21 | Category labels by what a message is | 11/11 | 11/11 | 224.0 | 245.2 | 53 | 46 | 708,420 | 884,752 |
| 22 | Newsletters lists decide Bulk | 9/9 | 9/9 | 89.3 | 95.4 | 26 | 19 | 672,623 | 565,065 |
| 23 | Mail meant for the user, not Bulk | 9/9 | 9/9 | 256.4 | 130.4 | 47 | 32 | 1,896,127 | 828,840 |
| 24 | Newsletter reaches the threshold | 10/10 | 10/10 | 110.9 | 120.9 | 21 | 19 | 640,136 | 479,241 |
| 25 | Learned newsletter conflicts with the user's line | 9/9 | 9/9 | 129.2 | 104.0 | 24 | 22 | 828,424 | 771,371 |
