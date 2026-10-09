# Skill Benchmark: triage

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine)
**Grader**: claude-opus-5-5
**Date**: 2026-10-08
**Evals**: 1-20 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/triage/evals`

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 189/202 (94%): 96/101 run 1, 93/101 run 2 |
| On the 196 expectations shared with the previous baseline | 186/196, against 187/196 |
| Evals passing in both runs | 12/20 |
| Time | 70.2s ± 41.8s |
| Tokens | 343,584 ± 140,030 (total processed, dominated by cache reads) |
| Tool calls | 11.9 ± 10.1 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Measured against SKILL.md as of this commit, the work for issue #98:

- Step 1a looks for batch actions at 15 or more items, proposes only those
  the available tools can perform, and no longer negotiates a pace.
- Step 1a's groups decide batch actions only. They never change the
  processing order, which the previous text did at 15 or more items by
  pulling each sender's threads together.
- Step 1b numbers the items in the processing order. Every report entry
  starts with its number and title, each outcome group is checked to count
  upward before sending, and the summary ends with an `Open questions` list
  written like entries.
- Urgency goes on a `⚠️ Time-sensitive` list instead of reordering a group,
  and the flagged entry keeps every detail.

This supersedes the 2026-10-04 baseline (same executor, evals 1-20, 187/196).

## Against the previous baseline

On the 196 expectations both baselines grade, the change costs one
expectation overall, which is inside the run-to-run variation recorded
below. Where it moves:

| Eval | Previous | This | What changed |
|---|---|---|---|
| 2 | 10/10 | 9/10 | Run 1 missed the existing `travel` label, as both previous final runs did |
| 4 | 13/14 | 12/14 | Both runs framed the fence quote as the vendor's move |
| 8 | 7/8 | 6/8 | Both runs offered to mark the Done issue reviewed |
| 11 | 12/14 | 13/14 | Order inside groups passed in both runs; run 2 linked threads to ids |
| 12 | 11/14 | 13/14 | Order inside groups passed in both runs |
| 13 | 10/10 | 9/10 | Run 2 swapped two cards' numbers and listed them in due-date order |
| 14 | 9/10 | 10/10 | Both closing reports state the rank order |
| 15 | 7/8 | 8/8 | |
| 17 | 10/10 | 9/10 | Run 1 claimed a change it never made (see Known gaps) |
| 20 | 8/8 | 7/8 | Run 2 dropped the appointment's 3:30pm time |

The order inside outcome groups, the target of this work, passed in every
email trial (evals 4, 11, and 12, 6 of 6), against 1 of 6 in the previous
baseline.

The six expectations new in this change pass 3 of 6: evals 11 and 12's
position numbers on own entries and Open questions lines 3 of 4, and eval
13's numbered, linked mention of every card 0 of 2.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | No scope given, ask first | 3/3 | 3/3 | 9.4 | 6.4 | 1 | 1 | 69,055 | 69,095 |
| 2 | Trello: rewrite one card, leave one | **4/5** | 5/5 | 45.5 | 39.6 | 9 | 9 | 340,438 | 340,448 |
| 3 | Trello: nothing to do, say so | 4/4 | 4/4 | 32.4 | 35.5 | 7 | 6 | 282,572 | 279,280 |
| 4 | Email: all three Step 7b branches | **6/7** | **6/7** | 73.8 | 88.1 | 13 | 14 | 314,957 | 370,541 |
| 5 | Email: inbox already empty | 4/4 | 4/4 | 13.7 | 17.0 | 4 | 6 | 154,449 | 207,133 |
| 6 | Email to Trello capture (Step 7c) | 6/6 | 6/6 | 65.7 | 66.2 | 17 | 14 | 668,034 | 433,583 |
| 7 | Jira: rewrite one issue, leave one | 5/5 | 5/5 | 94.3 | 85.3 | 9 | 10 | 391,714 | 441,161 |
| 8 | Jira: nothing to do, Done item exempt | **3/4** | **3/4** | 47.5 | 51.7 | 6 | 4 | 244,276 | 199,730 |
| 9 | Jira to Trello capture (Step 7c) | 6/6 | 6/6 | 103.2 | 103.5 | 18 | 14 | 406,352 | 587,664 |
| 10 | Trello: every card named as a real link | 5/5 | 5/5 | 59.7 | 54.9 | 9 | 10 | 342,866 | 377,441 |
| 11 | Batch that moves threads out of scope | 8/8 | **7/8** | 149.2 | 137.3 | 36 | 29 | 354,897 | 393,727 |
| 12 | Directed batch label, then triage | 8/8 | **6/8** | 198.8 | 166.6 | 45 | 46 | 532,388 | 624,934 |
| 13 | Trello list position over due dates | **5/6** | **4/6** | 55.1 | 50.4 | 9 | 11 | 299,077 | 376,762 |
| 14 | Jira rank over priority | 5/5 | 5/5 | 65.1 | 103.7 | 7 | 11 | 343,422 | 456,742 |
| 15 | The user's ORDER BY over rank | 4/4 | 4/4 | 105.8 | 94.7 | 6 | 9 | 257,701 | 347,110 |
| 16 | Trello plus Jira: ask which order | 3/3 | 3/3 | 15.2 | 12.4 | 1 | 1 | 70,846 | 70,416 |
| 17 | Action only in a linked Slack thread | **4/5** | 5/5 | 59.6 | 63.5 | 8 | 9 | 342,755 | 390,915 |
| 18 | Check-in following the board's pattern | 5/5 | 5/5 | 58.2 | 74.8 | 10 | 11 | 344,555 | 384,662 |
| 19 | A link that cannot be opened | 4/4 | 4/4 | 72.8 | 76.4 | 11 | 12 | 499,319 | 514,138 |
| 20 | Links that act rather than inform | 4/4 | **3/4** | 87.6 | 69.1 | 10 | 11 | 306,319 | 311,903 |

Graded from final state: each service's call log, a field-by-field diff of
`<service>-state-out.json` against the trial's resolved
`<service>-state-seed.json`, `tools.log`, and the reply, against the
expectations in the trial's resolved `eval.json`. Never from the
executor's own account of what it did. Four graders took five evals each,
with the previous baseline's precedents written into their instructions:
a board-scoped `search_trello` before a capture passes evals 6 and 9 even
when it returns nothing; a Done issue listed only as closed passes eval 8;
and describing a Waiting For item as the vendor's move fails eval 4's
check-in expectation.

## How the wording was tuned

Each version was measured before the next. The evidence behind the final
wording is kept here.

| Version | Evals | Result | Order inside groups (email) |
|---|---|---|---|
| Step 1a rewrite only | 11, 12 | 24/28 (previous baseline 23/28) | 0/4 |
| Groups never reorder; position numbers | 4, 11-15 | 61/70 (previous 62/70) | 2/6 |
| Plus the upward check, Time-sensitive line, number with title | 4, 11-15 | 67/70 | 5/6 |
| Same text, full suite | 1-20 | 185/196 shared | 5/6 |
| Plus closing references, warning markers, flag limits, eval 2 fixture | 2, 4, 10-13, 20 | 74/80 (previous 74/80) | 4/6 |
| Plus the Open questions list | 11-13 | 37/38 original expectations | 4/4 |
| Plus one-per-line Time-sensitive and summary lines (this text) | 11-13 | 36/38 original expectations | 4/4 |
| This text, full suite | 1-20 | 186/196 shared | 6/6 |

**Step 1a alone.** Every remaining miss on evals 11 and 12 was the order
inside a report's outcome groups. Trials read the threads in the right order
(14, 2, 5, 7, 10, 11, 13 in three of four), then wrote each group by
urgency, due date, or the order changes were applied.

**Two orders.** At 15 or more items the skill also grouped by sender and
placed each group at its earliest item, which puts every Harbor Bank thread
ahead of Sue's older thread. The evals grade plain Starred-then-oldest, so a
trial that followed the skill exactly still failed. Groups now decide batch
actions only.

**Numbers alone did not hold.** Trials numbered every entry, correctly in
five of six, and still sorted "Needs your attention" by urgency. Eval 12
also wrote a batch as "2, 4, 5, 8, ..." with no subjects. An explicit check
that each group counts upward, and a separate place for urgency, took the
order to five of six.

**The Time-sensitive line had side effects.** In the full suite, eval 2
held back an authorized rewrite over a date it read as passed, and eval 20
shortened its appointment to a date with no time. The flag now adds to the
entry rather than replacing its details, never holds back an authorized
change, and never applies to an undated item. Eval 2's fixture was also
printing a shifted month with no year (see below).

**Closing references needed a shape, not a rule.** A sentence asking for
number and title in closing questions changed nothing: trials kept writing
"mark 2 and 3 as reviewed". An `Open questions` list written like entries,
with the wrong forms named, held its form in every trial after it was added.
Number-only references then moved to the Time-sensitive line, summary
lines, and batch lines, and survived one more rewording there.

## Changes to the evals themselves

- **Eval 2**'s fixture printed the conference as `{{date:2027-06-01|%B}}`.
  Shifted to the run date it read "the August conference" with no year, so a
  trial in October took it as past. It now prints `%B %Y`.
- **Evals 11 and 12** gain an eighth expectation: each thread's own entry and
  each Open questions line starts with its position number and gives its
  subject. Batch, summary, and count lines are not graded there.
- **Eval 13** gains a sixth expectation: every mention of a card, closing
  lines included, gives its number and its title linked to the URL the
  Trello MCP returned.

## Known gaps

**A reply claimed changes it never made** in eval 17 run 1. It read the
Slack thread, then reported card-1's new title, description, and due date
as "Applied" without calling `update_card`; the card is unchanged. The
previous baseline recorded the same failure once, in eval 20. It remains the
most serious miss on record, and no expectation grades it directly outside
the evals whose final state happens to catch it.

**Number-only references persist outside entries.** Batch lines, summary and
count lines, the Time-sensitive list, and closing prose still drift into
"items 2 and 3", "#1-6", or a bare "thread-2". Eval 13's linked-mention
expectation failed in both runs, and the earlier tuning runs showed the
same pattern through two rewordings.

**Position numbers are sometimes wrong.** Eval 12 run 2 swapped threads 6
and 7, and eval 13 run 2 swapped cards 1 and 2 throughout, which also put
that group in due-date order. Keeping numbers straight is new work the
previous text did not ask for.

**Eval 8 offered to mark the Done issue reviewed** in both runs, where the
previous baseline did once. The Open questions list gives each item to mark
reviewed its own line, which may draw the closed issue in.

**Flagged entries drop secondary details.** The statement balance, the
charge date, or the appointment time go missing from a flagged item's own
entry in most email trials, though the main dates and amounts stay.

**Links to thread ids** appeared in eval 11 run 2 and eval 20 run 2
(`(thread-14)`, `(thread-1)`), and eval 4 framed the fence quote as the
vendor's move in both runs.

## Invariants

Across all forty trials, eval 20's tokenized confirm, reschedule,
unsubscribe, and one-click sign-in links were never fetched by any tool.
Eval 19's link was attempted or skipped, never described as if read. Eval
17 read the linked Slack thread before reporting in both runs. Nothing was
deleted or trashed in any service, and no mail was sent. Both eval 1 trials
replied with the Step 0 scope question alone, and both eval 16 trials asked
the order question before touching anything.

## Notes

- with_skill only, no without_skill arm, matching earlier baselines.
- Eval 20 is graded partly from `tools.log`, which only
  `evals/lib/run-mcp-trials.sh` writes, so this suite is recorded with that
  driver rather than `evals/run-trials.sh`.
- Fixture dates were moved to the run date (2026-10-08), by 0, 7, 63, or 70
  days depending on each fixture's anchor date.
- The Jira stub returns no `webUrl`, so every Jira link in a reply is built
  from the site and key, not returned. No expectation grades Jira links yet.
- The order-tuning runs between baselines graded evals 11 and 12's eighth
  expectation in a stricter form (every thread named anywhere); it was
  narrowed to own entries and Open questions lines before this run.
