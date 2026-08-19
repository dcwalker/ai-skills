# Skill Benchmark: triage

**Model**: claude-opus-5 (executor and analyzer)
**Date**: 2026-08-19T08:05:00Z
**Evals**: 1-10 (2 runs each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 93/94 (99%) — 47/47 run 1, 46/47 run 2 |
| Evals passing in both runs | 9/10 |
| Time | 45.2s ± 21.6s |
| Tokens | 387,790 ± 150,324 (total processed, dominated by cache reads) |
| Tool calls | 6.0 ± 4.0 |

Spreads are population standard deviations, the convention the other baselines
use. Tokens are total processed per trial (input + output + cache creation +
cache read) and are not comparable to the sub-agent token figures in the
software-development baselines; they are rounded to whole tokens, since four
decimal places on a token count is false precision that also reads as a long
digit run to a secret scanner.

Measured against SKILL.md as of this commit. An earlier measurement of the same
suite, before the four fixes below, scored 85/94 with 6/10 evals clean; see
"What was fixed". Evals 6 and 9 also had one expectation reworded, from naming
`search_trello` to grading the outcome; see "Grading the outcome, not the
tool".

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | No scope given — ask first | 3/3 | 3/3 | 5.2 | 5.4 | 0 | 0 | 94,308 | 94,302 |
| 2 | Trello: rewrite one card, leave one | 5/5 | **4/5** | 55.3 | 40.1 | 7 | 7 | 434,479 | 421,284 |
| 3 | Trello: nothing to do, say so | 4/4 | 4/4 | 38.2 | 35.5 | 5 | 5 | 418,381 | 373,393 |
| 4 | Email: all three Step 4b branches | 5/5 | 5/5 | 57.9 | 43.8 | 10 | 10 | 394,979 | 441,663 |
| 5 | Email: inbox already empty | 4/4 | 4/4 | 16.1 | 13.5 | 2 | 2 | 258,284 | 205,518 |
| 6 | Email → Trello capture (Step 4c) | 6/6 | 6/6 | 47.5 | 47.8 | 11 | 11 | 564,814 | 579,872 |
| 7 | Jira: rewrite one issue, leave one | 5/5 | 5/5 | 59.9 | 63.5 | 3 | 4 | 375,574 | 430,141 |
| 8 | Jira: nothing to do, Done item exempt | 4/4 | 4/4 | 43.8 | 44.8 | 2 | 2 | 321,215 | 258,740 |
| 9 | Jira → Trello capture (Step 4c) | 6/6 | 6/6 | 75.0 | 88.2 | 12 | 13 | 572,818 | 694,483 |
| 10 | Trello: every card named as a real link | 5/5 | 5/5 | 55.2 | 66.8 | 7 | 7 | 381,865 | 439,678 |

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

The priority half needed a second pass. It slipped once in eight post-fix runs
— a trial set `High` on a personal issue while correctly leaving assignee
unset — because the rule still led with "if not set, suggest a priority" and
put the personal-item exclusion third. The two halves now have the same shape:
the exclusion leads, and the same "skip the field, not the question" clarifier
that made the assignee rule hold 8 for 8 now sits on both.

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
before anything was created, by any means that returns them. Under the old
wording that trial scored 5/6; under the new one its `view_list` call reads as
the pass it always was, and across the four recorded runs of evals 6 and 9 the
trials split roughly evenly between `search_trello` and `view_list` with no
difference in what they actually established.

The one expectation deliberately left method-bound is eval 4's, which allow-lists
the writes an email triage may make (`create_draft`, `modify_thread_labels`,
`archive_thread`). There the enumeration is the point: an unrecognized write tool
appearing in that log is something a human should look at, not something the
expectation should quietly accept.

## Splitting SKILL.md into references/

SKILL.md was 773 lines, well past the ~500-line guideline. It is now 517, with
six `references/` files carrying 437 lines between them, each linked from the
step that needs it.

What moved was chosen by **conditionality**, not by size: material the run
consults only when a particular condition arises, rather than procedure every
run executes.

| File | Covers | Fires when |
|---|---|---|
| `email-triage.md` | Step 4b's decision tree, email corpus fetching | scope is an inbox |
| `gathering-context.md` | Steps 3, 5, 6 | the item has links, or a Tier 2/3 item warrants a search |
| `staleness-and-stalls.md` | Steps 7, 7a, 7b | the item has gone quiet |
| `field-guidance.md` | title/description/label calibration examples | proposing a rewrite |
| `sizing-and-tiers.md` | Steps 0.5 and 2a-2c signal tables | context or size is not obvious |
| `methodology.md` | GTD, the 2-minute rule, Kanban, LEAN | never — it is background |

Every rule the earlier fixes pinned down stayed inline, verbatim: the
empty-scope rule in Step 0, the assignee and priority rules in Step 4, Step
4c's source-edit and description rules, Step 8's hyperlink rule and the Quality
Rules list. What left Step 4 was the per-context *examples* ("for a personal
task…", "for a professional bug…"), not the rules that always apply.

`run-trials.sh` had to change with it: it staged `SKILL.md` alone, so after the
split every `references/` link in a trial's copy would have dangled. It now
stages `SKILL.md` **and** `references/` — still not the whole directory, which
would hand the trial `evals.json` and the fixtures.

**Measured, not assumed.** Six full passes ran after the split. The two
recorded here score 93/94 with 9 of 10 evals clean in both — identical to the
pre-split figure. The failures across all six were single-run misses in three
different evals (2, 7 and 10), never the same one twice.

Five of those six misses were in prose that never moved, so the split cannot
explain them. The exception is the one recorded above: run 2's eval 2 rewrote
card-1's title and never proposed the board's existing `travel` label. The
label *rule* is still inline; the per-context label *examples* are in
`field-guidance.md`. Nine of the ten recorded runs of that eval apply the
label, including run 1 here, so this is most likely the same run-to-run noise
as the other two — but it is the one miss the split could plausibly have
caused, and it is worth watching rather than dismissing.

## An eval-versus-skill disagreement, left open

**Eval 10, expectation 5** treats card-2 as an untouched control. Some runs
create a `travel` label — the board genuinely has none — and apply it to
card-2. The prompt says to apply anything the skill is confident about, and
Step 4's label rules apply to every card in scope, so "already well-formed" and
"off limits" are not the same thing. Other runs ask first, which is also
defensible; across ten recorded trials the split is three apply, seven ask or
leave it. Both runs recorded here left it alone. Left as-is: it is minor, and
both behaviours are reasonable readings of the prompt.

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
  root**, which is the default in most containers. The script now drops that
  flag entirely and always passes an explicit `--allowedTools`, matching
  `evals/lib/run-mcp-trials.sh`: `Bash Read Write Edit Glob Grep WebFetch
  TodoWrite Skill` plus every stub server named in the fixture's own
  `mcp-config.json`. One unconditional path rather than a root-only branch, so
  the tool surface cannot silently differ between the environment a baseline
  was recorded in and the one it is reproduced in.

  The non-MCP tools are load-bearing rather than filler. Step 1 and Step 4c
  each define an MCP → skill → CLI → REST hierarchy, and `run-mcp-eval.sh`
  goes to some trouble to isolate the two shell paths SKILL.md names — a
  `curl` to Jira's REST API, and `gh` — by scrubbing credentials and shadowing
  `gh`. Without `Bash` those tiers can never fire, which would have made an
  isolation the harness deliberately built unreachable.
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

Widening the allowlist changed no result: the suite scores the same 93/94 with
it as without, and across all twenty trials not one `gh` call reached the stub
and not one file was written to a workspace. That is the expected outcome rather
than a disappointment — every fixture wires up an MCP server, so the top tier of
the hierarchy is always available and correctly preferred. It does mean the CLI
and REST tiers are still untested by these fixtures: exercising them needs a
fixture that deliberately wires up **no** MCP server, which does not exist yet.
The allowlist removes a ceiling; it does not by itself add coverage.

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
rather than merely the invariant it grades. Every "leave this one alone" control held
in both runs: card-2 in evals 2 and 10, card-1 in evals 6 and 9, and HOME-2 in
evals 7 and 8 were all byte-identical to their seeds. Both eval-8
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
