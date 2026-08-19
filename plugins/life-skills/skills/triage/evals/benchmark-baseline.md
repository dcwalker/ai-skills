# Skill Benchmark: triage

**Model**: claude-opus-5 (executor and analyzer)
**Date**: 2026-08-19T04:40:00Z
**Evals**: 1-10 (2 runs each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 93/94 (99%) — 46/47 run 1, 47/47 run 2 |
| Evals passing in both runs | 9/10 |
| Time | 46.7s ± 22.1s |
| Tokens | 413,080 ± 164,708 (total processed, dominated by cache reads) |
| Tool calls | 6.8 ± 4.2 |

Spreads are population standard deviations, the convention the other baselines
use. Tokens are total processed per trial (input + output + cache creation +
cache read) and are not comparable to the sub-agent token figures in the
software-development baselines.

Measured against SKILL.md as of this commit. An earlier measurement of the same
suite, before the four fixes below, scored 85/94 with 6/10 evals clean; see
"What was fixed". Evals 6 and 9 also had one expectation reworded after these
trials ran; both runs were re-graded from their recorded call logs, and the
change is described under "Grading the outcome, not the tool".

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | No scope given — ask first | 3/3 | 3/3 | 4.8 | 5.8 | 0 | 0 | 94,829 | 94,798 |
| 2 | Trello: rewrite one card, leave one | 5/5 | 5/5 | 55.7 | 45.8 | 7 | 9 | 392,365 | 611,919 |
| 3 | Trello: nothing to do, say so | 4/4 | 4/4 | 31.9 | 35.8 | 5 | 5 | 385,807 | 385,966 |
| 4 | Email: all three Step 4b branches | 5/5 | 5/5 | 59.1 | 46.5 | 12 | 12 | 458,270 | 452,824 |
| 5 | Email: inbox already empty | 4/4 | 4/4 | 18.9 | 15.6 | 2 | 2 | 209,166 | 207,771 |
| 6 | Email → Trello capture (Step 4c) | 6/6 | 6/6 | 47.7 | 42.1 | 11 | 10 | 520,999 | 579,900 |
| 7 | Jira: rewrite one issue, leave one | 5/5 | 5/5 | 72.2 | 69.2 | 5 | 6 | 399,480 | 506,231 |
| 8 | Jira: nothing to do, Done item exempt | 4/4 | 4/4 | 46.8 | 54.9 | 4 | 3 | 325,094 | 323,414 |
| 9 | Jira → Trello capture (Step 4c) | 6/6 | 6/6 | 81.9 | 81.7 | 12 | 15 | 665,388 | 679,619 |
| 10 | Trello: every card named as a real link | **4/5** | 5/5 | 63.7 | 54.3 | 9 | 7 | 518,074 | 449,693 |

Graded from final state — each service's call log, and a field-by-field diff of
`<service>-state-out.json` against the fixture's seed — never from the
executor's own account of what it did. Trials ran three at a time, so the times
carry some contention.

## What was fixed

The previous measurement found four defects that reproduced across runs. All
four are gaps in SKILL.md rather than lapses of model judgment, and all four are
closed in this commit.

**An empty scope was not a finished run** (eval 5, failed both pre-fix runs).
`in:inbox` returned zero threads and both trials went looking anyway — `""`,
then `in:anywhere` — and reported the account's one archived receipt back to the
user. Step 0 had a great deal to say about *establishing* scope and nothing
about a confirmed scope turning out to be empty, and both trials filled that
silence the same way. Step 0 now says an empty scope is a complete answer:
report it, name what you searched, and do not re-query or widen without being
asked. Both post-fix runs stop at two read calls and say so out loud — "an empty
scope is a complete result, not something to work around."

**"Skip this" read as "do it without asking"** (eval 7, failed both pre-fix
runs). Both trials set assignee and priority on a personal Jira issue, against
the skill's own text — "For personal boards where the user is the only member,
skip this" and "Skip for personal tasks". Because that assignee sentence
followed "ask who should own it", the nearest antecedent was the *asking*, so
the trials skipped the question and set the field. Both rules now name the
outcome instead: leave the field unassigned, leave priority unset, and "skip the
field, not the question". Post-fix, both runs leave both fields alone and
explain why unprompted.

**A capture licensed an edit to its source** (eval 9, failed both pre-fix runs).
After lifting three untracked to-dos out of HOME-7's description onto Trello,
both trials rewrote that description to trim the prose they had just extracted.
Step 4c covered searching, matching, creating and confirming, and said nothing
about whether the source item could be touched. It now has an explicit rule: a
capture is not a license to edit the source, the original wording is the record,
and a comment is where a capture gets noted. Post-fix, both runs add a comment
and leave every HOME-7 field alone — run 2's reply: "Left the original HOME-7
description untouched and added a comment on the issue instead."

**Capture cards were created without descriptions** (eval 9, failed one pre-fix
run, then a second time on re-test). Step 4c's description bullet — "include a
link back to the source item being triaged" — was being dropped whenever one
source produced several cards, so the back-link survived only in the chat reply.
Worse, the reply then *claimed* the cards linked back when they did not. The
bullet is now marked required, calls out the several-cards case, and forbids
claiming a link in the summary that is not on the card. Across four post-fix
trials of evals 6 and 9, every capture card carries its source link.

## Grading the outcome, not the tool

Evals 6 and 9 each opened with an expectation naming `search_trello` as the call
that had to precede `create_card`. That grades a method, and the method is the
part most likely to change: Step 4c itself offers a four-level hierarchy — MCP,
skill, CLI, REST — and says "Trello MCP `search_trello` **or equivalent**". A
trial that reads the destination list with `view_list`, a `trello-tools` CLI
call, or a tool that does not exist yet has done the thing the step asks for.

Run 1 of eval 9 did exactly that and failed the expectation while satisfying its
intent, with its own reply confirming the duplicate check. Both expectations are
now written against the outcome — the destination's existing cards were read
before anything was created, by any means that returns them — and both runs were
re-graded from their recorded call logs under the new wording. Nothing about the
runs changed; run 1's eval 9 goes from 5/6 to 6/6, and its `view_list` call now
reads as the pass it always was.

The one expectation deliberately left method-bound is eval 4's, which allow-lists
the writes an email triage may make (`create_draft`, `modify_thread_labels`,
`archive_thread`). There the enumeration is the point: an unrecognized write tool
appearing in that log is something a human should look at, not something the
expectation should quietly accept.

## The one remaining failure is an eval-versus-skill disagreement

**Eval 10, expectation 5** treats card-2 as an untouched control. Run 1 created a
`travel` label — the board genuinely had none — and applied it to card-2. The
prompt said to apply anything the skill was confident about, and Step 4's label
rules apply to every card in scope, so "already well-formed" and "off limits"
are not the same thing. Run 2 asked first instead, which is also defensible.
Across five recorded trials of this eval the split is three apply, two ask.
Left as-is: it is minor, and both behaviours are reasonable readings of the
prompt.

## Hyperlink discipline stops at Trello

Eval 10 is the newest eval in the suite: every card named in a summary must be a
hyperlink to the URL the MCP server actually returned. Both runs pass it on the
Trello side, including the "no changes needed" card, and neither invented a URL.

It collapses on Gmail. The Gmail stub returns no `url` field on a thread, and
lines 654-656 say exactly what to do in that case: "Only ever use a URL the
platform actually returned — if an item's URL is unavailable, say so and name
the item in plain text rather than constructing one." Across the recorded runs
every attempt to name a thread broke that rule in one of two directions — a bare
id as the link target (`[School fair volunteering rota](thread-1)`,
`[Q3 forecast numbers](thread-1)`) or a fabricated one
(`https://mail.google.com/mail/#inbox/thread-1`, which is the right shape for
real Gmail and still a URL the server never returned). Nobody took the
plain-text fallback the rule prescribes.

This is precisely the failure eval 10 was written to catch, occurring on the two
services eval 10 does not cover — and the Trello half passes only because the
Trello stub does return `url`. The suite needs a Gmail equivalent and a Jira
equivalent; until it has them, eval 10's pass overstates how well the rule
holds. This one is left open deliberately: it is an eval gap first, and the
right fix is an expectation that grades it, not more prose in a skill that
already says the right thing.

## The harness could not run as checked in

`run-trials.sh` is the documented way to run this suite, and it failed three
ways here before producing anything. All three are fixed:

- **`--dangerously-skip-permissions` is refused outright when the shell is
  root**, which is the default in most containers. The script now allow-lists
  exactly the stub servers the fixture wired into `mcp-config.json` when
  `$EUID` is 0, which gets the same reach without the flag.
- **The subprocess could not see the skill.** It runs with cwd inside
  `$WORKSPACE_DIR`, where nothing loads this repo's plugins — probing a trial
  returned no `triage` skill at all, so the suite would have been measuring the
  bare model. The script now stages `SKILL.md` alone into
  `$WORKSPACE_DIR/.claude/skills/triage/`; copying the directory would put
  `evals.json` and `fixtures/` inside the workspace and hand the trial its own
  answer key.
- **stdin was never redirected**, so every trial burned three seconds on "no
  stdin data received" before starting. Now `< /dev/null`.

The header comment claiming nested `claude` subprocesses cannot authenticate
from an in-session Bash call was also wrong in this environment — every trial
recorded here ran that way — so it now says so conditionally rather than as a
blanket prohibition.

One thing left as a flag rather than a fix: the default `.trial-runs/` sits
under `evals/`, which leaves `evals.json` and `fixtures/` three directories
above each trial's own cwd, in reach of an executor that goes looking. The
script now honours a `TRIALS_DIR` override and every graded run used it to put
the workspaces outside the repo entirely.

## Invariants

Nothing was deleted or trashed in any service across either run — no
`trash_thread`, no card or issue deletion, no `transitionJiraIssue`. No mail was
sent: every reply went to `create_draft`, which is also all the real Gmail MCP
allows. Both eval-1 trials made **zero** tool calls and answered with the Step 0
scope question verbatim, which is the preferred shape that eval's notes describe
rather than merely the invariant it grades. Every "leave this one alone" control
held except eval 10 run 1: card-2 in eval 2, card-1 in eval 6, card-1 in eval 9
and HOME-2 in evals 7 and 8 were all byte-identical to their seeds. Both eval-8
trials treated the Done issue as closed and proposed nothing for it.

## Notes

- with_skill only, no without_skill arm, matching the previous baseline.
- The `create_card` stub accepts `name` as either a string or a list, for schema
  parity with the real Trello MCP. Earlier trials used the batch form; both runs
  here created cards one at a time.
- This supersedes the 2026-07-31 sonnet baseline (9 evals, 42/42). That run is
  not directly comparable — different executor model, and eval 10 is new — but
  it is worth recording that it praised eval 9 for "flagg[ing] a now-stale
  sentence in the Jira description instead of silently rewriting it", the exact
  behaviour that regressed here and is now pinned down by an explicit rule
  rather than left to the model.
- Still deferred, unchanged from the previous baseline: staleness handling
  (Step 7) needs last-activity modelling in the Trello stub, and large-set batch
  pacing (Step 0.5) has no fixture. Both eval-8 trials reasoned about HOME-1's
  20-day silence off the Jira stub's `updated` timestamps, so the Jira half of
  Step 7 is at least exercised.
