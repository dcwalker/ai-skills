# Skill Benchmark: triage

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine)
**Grader**: claude-opus-5-5
**Date**: 2026-10-03
**Evals**: 1-20 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/triage/evals`

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 183/196 (93%): 92/98 run 1, 91/98 run 2 |
| Evals passing in both runs | 12/20 |
| New evals 13-20 | 68/70 |
| Time | 65.0s ± 41.1s |
| Tokens | 474,710 ± 178,888 (total processed, dominated by cache reads) |
| Tool calls | 12.5 ± 11.2 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Measured against SKILL.md as of this commit, the work for issue #90: a
processing order (Step 1b), following links before naming each item's action
(Steps 5a and 6), an action that is always the user's own, and links that act
rather than inform never being opened.

This supersedes the 2026-08-19 baseline (claude-opus-5, evals 1-10, 93/94). That
figure is not comparable with this one: the executor model differs, the
fixtures have aged by six weeks (see "Fixture dates have drifted"), and the
suite has grown. The comparison that matters is the next section.

## Against main, same day, same executor

Main was measured on the same machine and date, with the same executor, from a
worktree of `origin/main` running its own evals.json, stubs, and fixtures. On
the 59 expectations evals 1-12 have in common:

| | Run 1 | Run 2 | Total |
|---|---|---|---|
| main | 56/59 | 56/59 | 112/118 |
| this branch | 54/59 | 57/59 | 111/118 |

The one-expectation gap is inside run-to-run noise: no shared expectation fails
on the branch in both runs that passes on main in both. The four expectations
this change adds to evals 4, 11, and 12 score 4/8; see "Known gaps".

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | No scope given, ask first | 3/3 | 3/3 | 5.6 | 6.0 | 1 | 1 | 108,001 | 107,981 |
| 2 | Trello: rewrite one card, leave one | 5/5 | 5/5 | 43.7 | 138.4 | 9 | 9 | 492,059 | 429,102 |
| 3 | Trello: nothing to do, say so | 4/4 | 4/4 | 48.1 | 35.8 | 8 | 8 | 428,532 | 425,495 |
| 4 | Email: all three Step 7b branches | **6/7** | **6/7** | 79.3 | 91.3 | 14 | 16 | 463,545 | 526,034 |
| 5 | Email: inbox already empty | 4/4 | 4/4 | 16.3 | 18.8 | 5 | 5 | 235,691 | 236,214 |
| 6 | Email to Trello capture (Step 7c) | 6/6 | 6/6 | 53.8 | 48.4 | 13 | 13 | 595,756 | 439,204 |
| 7 | Jira: rewrite one issue, leave one | **4/5** | **4/5** | 73.0 | 68.2 | 9 | 6 | 503,034 | 430,674 |
| 8 | Jira: nothing to do, Done item exempt | **3/4** | **3/4** | 51.9 | 71.1 | 4 | 8 | 294,772 | 503,038 |
| 9 | Jira to Trello capture (Step 7c) | 6/6 | 6/6 | 94.6 | 89.0 | 17 | 22 | 721,550 | 910,324 |
| 10 | Trello: every card named as a real link | **3/5** | 5/5 | 52.0 | 54.8 | 9 | 10 | 493,548 | 548,232 |
| 11 | Batch that moves threads out of scope | 7/7 | **6/7** | 144.1 | 134.4 | 36 | 33 | 560,406 | 557,210 |
| 12 | Directed batch label, then triage | **6/7** | **6/7** | 177.6 | 178.1 | 52 | 50 | 928,498 | 677,320 |
| 13 | Trello list position over due dates | 5/5 | 5/5 | 35.2 | 35.9 | 9 | 9 | 366,928 | 428,090 |
| 14 | Jira rank over priority | 5/5 | **4/5** | 81.6 | 79.6 | 10 | 9 | 572,532 | 508,751 |
| 15 | The user's ORDER BY over rank | 4/4 | 4/4 | 62.1 | 72.7 | 6 | 5 | 362,090 | 363,064 |
| 16 | Trello plus Jira: ask which order | 3/3 | 3/3 | 16.8 | 14.2 | 2 | 2 | 171,741 | 170,885 |
| 17 | Action only in a linked Slack thread | 5/5 | 5/5 | 48.6 | 49.8 | 11 | 11 | 562,260 | 563,994 |
| 18 | Check-in following the board's pattern | 5/5 | 5/5 | 36.2 | 41.9 | 11 | 11 | 492,434 | 545,315 |
| 19 | A link that cannot be opened | 4/4 | 4/4 | 54.5 | 58.4 | 12 | 12 | 645,129 | 651,895 |
| 20 | Links that act rather than inform | 4/4 | **3/4** | 63.7 | 73.4 | 10 | 10 | 447,086 | 519,967 |

Graded from final state: each service's call log, a field-by-field diff of
`<service>-state-out.json` against the fixture's seed, `tools.log` for eval 20,
and the reply. Never from the executor's own account of what it did. Trials ran
two at a time.

## How the wording was tuned

Four versions of the skill text were measured before this one was recorded.
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
listing from the bottom up, and Step 9 says not to regroup the summary by
outcome. Shared expectations reached parity with main (113/118 against
112/118), but eval 16 still failed 0/3 in both runs. No trial ever read
`references/processing-order.md`, so the ask rule had to live in SKILL.md
itself.

**Third version (one targeted pass, then two full passes).** The two-source
ask rule moved into Step 0 as a gate parallel to `Confirmed: pending`, and the
Quality Rules gained it. Eval 16 went to 3/3 in every run. Shared expectations
fell to 98/118, though. Trials began asking for confirmation they had already
been given (evals 4, 6, and 11 wrote nothing despite the prompt's
authorization), as if the gate applied to every scope.

**This version.** The Step 0 rule now applies only when the scope itself
names two ordered sources, and says that any other scope's up-front
authorization goes ahead. The Quality Rules say outright that confirmation
given up front counts, and that one open question never holds back the other
changes. Step 6 says a date that has passed is flagged rather than holding the
item. Eval 16 stayed 3/3, and shared expectations returned to parity.

## Changes to the evals themselves

- **Eval 17**'s board offered a `health` label that the control card (call the
  dentist) fitted, so trials labelled it and failed "card-2 is not modified".
  The fixture no longer has that label.
- **Eval 18**'s expectation that the two existing check-ins are "not modified"
  was too strict: both fit an existing label, and adding one is ordinary
  triage. It now checks their titles, due dates, and lists.
- **Evals 11 and 12** star thread-14, so the inbox order has a Starred thread
  to put first.

## Known gaps

**An inbox reply groups threads by outcome, not by order.** Every trial of
evals 11 and 12 states the order, Starred first and then oldest first, and
most work the threads in it. Most replies still present them under headings
such as "needs your attention" or "archived with labels", so the
unrecognized-charge thread or the statement comes before the starred
picture-day thread. Three of the four eval 11 and 12 runs miss the order
expectation this way.

**A Waiting For thread is still framed as the vendor's move** in one of two
eval 4 runs ("it's on the vendor now, not you"), even when the reply goes on
to offer a follow-up date. Eval 18, where the board already has a check-in
pattern, passes in every run, so the gap is an email scope with no pattern to
copy.

**The order is not always said.** One of two eval 14 runs presents the issues
in rank order without saying so.

**Fixture dates have drifted.** Evals 6, 7, and 8 were written in July and
August around dates that have now passed: a school fair on 19 September, a
boiler service due 1 October, an insurance renewal due 10 September. Trials
now stop to ask whether those still stand. That is reasonable behaviour, and it
is what costs eval 8 its "HOME-1 looks complete" expectation in both runs and
eval 7 one expectation. Main shows the same hesitation on eval 8. Moving the
fixture dates forward, or writing them relative to the run date, would stop
the suite measuring the calendar.

**Smaller single-run misses.** Eval 7 run 2 assigned HOME-1 to the user "for
consistency with HOME-2", an invented assignee. Eval 10 run 1 named both cards
in plain text with no links. Eval 20 run 2 omitted the 3:30pm time from the
appointment action. Eval 4 run 1 said "Inbox is now empty" while leaving one
thread in it.

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
