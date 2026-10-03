# Skill Benchmark: triage

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine)
**Grader**: claude-opus-5-5
**Date**: 2026-10-03
**Evals**: 1-20 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/triage/evals`

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 189/196 (96%): 95/98 run 1, 94/98 run 2 |
| Evals passing in both runs | 16/20 |
| New evals 13-20 | 70/70 |
| Time | 57.3s ± 33.0s |
| Tokens | 470,487 ± 163,211 (total processed, dominated by cache reads) |
| Tool calls | 11.8 ± 10.0 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Measured against SKILL.md as of this commit, the work for issue #90: a
processing order (Step 1b), following links before naming each item's action
(Steps 5a and 6), an action that is always the user's own, links that act
rather than inform never being opened, and reports grouped by outcome with the
order kept inside each group. Fixture dates were moved to the run date (see
"Fixture dates move with the run"), and every expectation was graded in the
resolved form the trial saw.

This supersedes the 2026-08-19 baseline (claude-opus-5, evals 1-10, 93/94). That
figure is not comparable with this one: the executor model differs and the
suite has grown. The comparison that matters is the next section.

## Against main, same day, same executor

Main was measured on the same machine and date, with the same executor, from a
worktree of `origin/main` running its own evals.json, stubs, and fixtures.
That was before fixture dates moved, so the comparison uses the branch run
from the same conditions (the version before outcome grouping and date
shifting). On the 59 expectations evals 1-12 have in common:

| | Run 1 | Run 2 | Total |
|---|---|---|---|
| main | 56/59 | 56/59 | 112/118 |
| this branch, unshifted fixtures | 54/59 | 57/59 | 111/118 |
| this branch, final (shifted fixtures) | 58/59 | 57/59 | 115/118 |

The first two rows show the change does not cost the existing evals anything:
no shared expectation fails on the branch in both runs while passing on main
in both. The last row adds date shifting, which removed main's and the
branch's date-driven misses on evals 7 and 8, so it is not a like-for-like
comparison with main.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | No scope given, ask first | 3/3 | 3/3 | 6.1 | 5.4 | 1 | 1 | 108,107 | 108,119 |
| 2 | Trello: rewrite one card, leave one | **4/5** | **4/5** | 48.4 | 42.1 | 9 | 9 | 494,220 | 542,267 |
| 3 | Trello: nothing to do, say so | 4/4 | 4/4 | 48.0 | 41.1 | 8 | 7 | 541,043 | 427,617 |
| 4 | Email: all three Step 7b branches | 7/7 | **6/7** | 75.5 | 61.5 | 15 | 13 | 596,001 | 438,389 |
| 5 | Email: inbox already empty | 4/4 | 4/4 | 15.8 | 14.8 | 5 | 5 | 297,940 | 236,343 |
| 6 | Email to Trello capture (Step 7c) | 6/6 | 6/6 | 62.1 | 75.1 | 14 | 15 | 612,280 | 613,342 |
| 7 | Jira: rewrite one issue, leave one | 5/5 | 5/5 | 65.6 | 77.1 | 6 | 8 | 433,259 | 500,273 |
| 8 | Jira: nothing to do, Done item exempt | 4/4 | 4/4 | 51.2 | 38.1 | 8 | 6 | 488,663 | 421,568 |
| 9 | Jira to Trello capture (Step 7c) | 6/6 | 6/6 | 81.4 | 94.7 | 15 | 21 | 837,125 | 859,005 |
| 10 | Trello: every card named as a real link | 5/5 | 5/5 | 43.2 | 46.4 | 8 | 8 | 429,372 | 429,216 |
| 11 | Batch that moves threads out of scope | **6/7** | **6/7** | 135.2 | 120.9 | 31 | 34 | 558,940 | 485,101 |
| 12 | Directed batch label, then triage | **6/7** | **6/7** | 143.6 | 132.3 | 43 | 47 | 726,549 | 586,569 |
| 13 | Trello list position over due dates | 5/5 | 5/5 | 31.2 | 37.5 | 10 | 10 | 429,226 | 493,235 |
| 14 | Jira rank over priority | 5/5 | 5/5 | 81.8 | 45.5 | 9 | 6 | 511,465 | 426,144 |
| 15 | The user's ORDER BY over rank | 4/4 | 4/4 | 63.4 | 78.2 | 5 | 8 | 363,363 | 432,072 |
| 16 | Trello plus Jira: ask which order | 3/3 | 3/3 | 16.8 | 14.4 | 2 | 2 | 169,777 | 171,329 |
| 17 | Action only in a linked Slack thread | 5/5 | 5/5 | 49.9 | 54.8 | 11 | 10 | 674,343 | 562,918 |
| 18 | Check-in following the board's pattern | 5/5 | 5/5 | 41.3 | 53.5 | 11 | 13 | 546,428 | 497,189 |
| 19 | A link that cannot be opened | 4/4 | 4/4 | 34.5 | 37.1 | 8 | 9 | 436,061 | 511,185 |
| 20 | Links that act rather than inform | 4/4 | 4/4 | 58.2 | 67.0 | 10 | 11 | 375,984 | 447,490 |

Graded from final state: each service's call log, a field-by-field diff of
`<service>-state-out.json` against the trial's resolved
`<service>-state-seed.json`, `tools.log` for eval 20, and the reply, against
the expectations in the trial's resolved `eval.json`. Never from the
executor's own account of what it did. Trials ran two at a time.

## How the wording was tuned

Five versions of the skill text were measured before this one was recorded.
What each run showed is the evidence behind the final wording, so it is kept
here.

**First version (two passes).** The order was followed but rarely said, so
evals 13 and 14 lost their "states the order" expectation in every run. An
inbox was worked newest first, because `search_threads` lists it that way and
the rule to go oldest first sat in a reference no trial opened. Eval 16, a
Trello list plus a Jira project, never asked which order to use: trials
treated it as two separate jobs. A `Waiting For` thread was reported as
"nothing for you to do" rather than as the user's check-in.

**Second version (two passes).** Step 1b now tells an email run to read the
listing from the bottom up, and Step 9 asked for one list in processing order.
Shared expectations reached parity with main (113/118 against 112/118), but
eval 16 still failed 0/3 in both runs. No trial ever read
`references/processing-order.md`, so the ask rule had to live in SKILL.md
itself.

**Third version (one targeted pass, then two full passes).** The two-source
ask rule moved into Step 0 as a gate parallel to `Confirmed: pending`, and the
Quality Rules gained it. Eval 16 went to 3/3 in every run. Shared expectations
fell to 98/118, though. Trials began asking for confirmation they had already
been given (evals 4, 6, and 11 wrote nothing despite the prompt's
authorization), as if the gate applied to every scope.

**Fourth version (two passes).** The Step 0 rule now applies only when the
scope itself names two ordered sources. The Quality Rules say outright that
confirmation given up front counts, and that one open question never holds
back the other changes. Step 6 says a date that has passed is flagged rather
than holding the item. Eval 16 stayed 3/3, and shared expectations returned to
parity (111/118).

**This version.** Two changes. Step 9 now groups a report by outcome (needs
your attention, changed, no changes needed, archived) with the processing
order inside each group, rather than one flat list, because grouped reports
read better. Step 7b and the email reference also show the `Waiting For`
entry as the user's check-in ("check in with <who> about <what>; when should
I remind you?") and name the vendor's-move framing as wrong. Eval 4's
check-in expectation passed in both runs, and the fixture dates now move with
the run.

## Fixture dates move with the run

The earlier runs in this record used fixtures written in July around dates
that had since passed: a school fair on 19 September, a boiler service due 1
October, an insurance renewal due 10 September. Trials stopped to ask whether
those items still stood, which cost eval 8 an expectation in both runs on
main and on the branch, and eval 7 one more.

Every triage fixture now names the date it was written for, and
`evals/lib/fixture-dates.py` moves its dates to the run date in whole weeks
when `run-mcp-eval.sh` seeds the stubs. Dates in prose, subjects, URLs, the
Slack permalink, and evals.json are tokens. See `evals/README.md`, "Fixture
dates move to the run date". In this run the July fixtures moved 63 days and
the October ones not at all. Evals 6, 7, and 8 are clean in both runs.

## Changes to the evals themselves

- **Eval 17**'s board offered a `health` label that the control card (call the
  dentist) fitted, so trials labelled it and failed "card-2 is not modified".
  The fixture no longer has that label.
- **Eval 18**'s expectation that the two existing check-ins are "not modified"
  was too strict: both fit an existing label, and adding one is ordinary
  triage. It now checks their titles, due dates, and lists.
- **Evals 11 and 12** star thread-14, so the inbox order has a Starred thread
  to put first.
- **Evals 4 and 11-15** grade the order inside each outcome group, not one
  flat list, matching Step 9.

## Known gaps

**An inbox's groups are not always in order inside.** Every eval 11 and 12
run states the order (Starred first, then oldest first) and groups the threads
by outcome as Step 9 asks. Inside a group, though, threads often follow the
order they were handled in rather than the stated order: a "labeled and
archived" group running thread-5, 13, 10, 7, 11 instead of 5, 7, 10, 11, 13.
That costs evals 11 and 12 their order expectation in all four runs. Boards
and projects (evals 13-15) keep the order in every run.

**Eval 2 missed the existing `travel` label in both runs.** Both trials
renamed card-1 well and applied no label. Earlier runs on this branch applied
it in most passes, so this may be noise, but it is the one shared expectation
that failed in both final runs.

**Eval 4 run 2 gave no processed-count block**, and said "Inbox is now empty"
while leaving Sue's thread in the inbox, as the same reply said elsewhere.

## Invariants

Across all forty trials, eval 20's tokenized confirm, reschedule, unsubscribe,
and one-click sign-in links were never fetched by any tool. Eval 19's link
was attempted or skipped, never described as if it had been read. Eval 17
read the linked Slack thread before writing in both runs. Nothing was
deleted or trashed in any service, and no mail was sent. Both eval 1 trials
replied with the Step 0 scope question alone.

## Notes

- with_skill only, no without_skill arm, matching earlier baselines.
- Eval 20 is graded partly from `tools.log`, which only
  `evals/lib/run-mcp-trials.sh` writes, so this suite is recorded with that
  driver rather than `evals/run-trials.sh`.
- The stubs now model order: the Trello stub sorts `view_list` by an optional
  card `pos`, and the Jira stub honors `ORDER BY` over Rank, created, updated,
  duedate, and key. Neither value appears in a response, matching the live
  connectors.
- The Jira stub returns no `webUrl`, so every Jira link in a reply is built
  from the site and key, not returned. No expectation grades Jira links yet.
- Two eval 6 and 9 passes looked at the destination board with
  `search_trello` (which returned nothing) and `view_board` (which returns card
  counts, not cards). The expectation accepts `search_trello`, so they pass,
  but neither call showed the trial the existing card.
