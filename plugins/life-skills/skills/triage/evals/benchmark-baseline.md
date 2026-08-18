# Skill Benchmark: triage

**Model**: claude-opus-5 (executor and analyzer)
**Date**: 2026-08-19T00:40:00Z
**Evals**: 1-10 (2 runs each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 85/94 (90%) — 43/47 run 1, 42/47 run 2 |
| Evals passing in both runs | 6/10 |
| Time | 47.9s ± 21.2s |
| Tokens | 406,852 ± 152,531 (run 2 only; total processed, dominated by cache reads) |
| Tool calls | 6.8 ± 4.0 |

Spreads are population standard deviations, the convention the other baselines
use. Tokens are total processed per trial (input + output + cache creation +
cache read) and are not comparable to the sub-agent token figures in the
software-development baselines.

This supersedes the 2026-07-31 sonnet baseline (9 evals, 42/42). It is not a
like-for-like comparison — different executor model, and eval 10 is new — but
three evals that scored full marks there fail here, and one of them fails for a
behaviour that baseline explicitly praised. See "Three failures, all
reproducible" below.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|
| 1 | No scope given — ask first | 3/3 | 3/3 | 14.6 | 5.1 | 0 | 0 | 94,260 |
| 2 | Trello: rewrite one card, leave one | 5/5 | 5/5 | 51.5 | 38.4 | 7 | 7 | 384,834 |
| 3 | Trello: nothing to do, say so | 4/4 | 4/4 | 40.9 | 34.0 | 5 | 5 | 382,546 |
| 4 | Email: all three Step 4b branches | 5/5 | 5/5 | 68.9 | 58.6 | 11 | 11 | 394,907 |
| 5 | Email: inbox already empty | **3/4** | **3/4** | 29.4 | 21.7 | 4 | 4 | 263,572 |
| 6 | Email → Trello capture (Step 4c) | 6/6 | 6/6 | 53.1 | 42.1 | 11 | 11 | 515,843 |
| 7 | Jira: rewrite one issue, leave one | **4/5** | **4/5** | 59.8 | 54.5 | 3 | 3 | 384,205 |
| 8 | Jira: nothing to do, Done item exempt | 4/4 | 4/4 | 49.9 | 53.6 | 5 | 6 | 435,906 |
| 9 | Jira → Trello capture (Step 4c) | **4/6** | **4/6** | 96.4 | 85.9 | 11 | 16 | 707,374 |
| 10 | Trello: every card named as a real link | 5/5 | **4/5** | 50.2 | 49.1 | 7 | 9 | 505,072 |

Graded from final state — each service's call log, and a field-by-field diff of
`<service>-state-out.json` against the fixture's seed — never from the
executor's own account of what it did. Run 2's time and token figures are the
subprocess's own; run 1 ran in plain-text output mode, so its times are derived
from artifact mtimes and it has no token figures. The mtime method was
validated against measured elapsed on evals 8, 9 and 10 (50/50, 97/97, 51/50).

Trials ran three at a time, so the times carry some contention.

## Three failures, all reproducible

Evals 5, 7 and 9 failed identically in both runs. None is a flake, and each is
a gap in SKILL.md rather than in the model's judgment.

### Eval 5 — an empty scope is not treated as a finished run

`in:inbox` returns zero threads. Both trials then ran two more searches — `""`
and `in:anywhere` — and reported the account's one archived receipt back to the
user by subject, sender and label. Nothing was written and neither trial
proposed work on it, so three of four expectations hold; the fourth forbids
expanding into archived mail unasked.

The skill has a great deal to say about *establishing* scope (Step 0's whole
Scope Confirmation design) and nothing at all about what to do when the
confirmed scope turns out to be empty. Both trials filled that silence the same
way: widen until something is found. A sentence in Step 0 — an empty scope is a
complete answer, report it and stop, do not widen without asking — would close
it.

### Eval 7 — "skip this" read as "do it without asking"

HOME-1 is a personal Jira issue with a one-word summary. Both trials rewrote the
summary correctly and derived the due date honestly from the description's
end-of-August quote deadline. Both also set **assignee** to the only user on the
instance and **priority** to High.

SKILL.md says not to:

- line 306, on assignee: "For personal boards where the user is the only member,
  skip this."
- line 319, on priority: "Skip for personal tasks."

Run 2's own reply shows the reasoning — it lists "Assignee | unassigned → Dan
Walker" as a change it is proud of. The instruction is being read as *skip the
question*, not *skip the field*. That reading is available because "skip this"
follows the sentence "ask who should own it", so the nearest antecedent is the
asking. Naming the outcome instead — "leave it unassigned" and "leave priority
unset" — removes the ambiguity.

### Eval 9 — the source item gets edited after a capture

Step 4c captures three untracked to-dos out of HOME-7's description onto Trello.
Both trials then called `editJiraIssue` to rewrite HOME-7's description, trimming
the prose that said those to-dos were untracked. Every other field — summary,
status, labels, priority, assignee, due date — was left alone, and the comment
both trials added is explicitly permitted; the description edit is not.

The edit is defensible bookkeeping, which is the point: Step 4c's four steps
cover searching, matching, creating and confirming, and say nothing about
whether the source item may be touched. The previous sonnet baseline recorded
the opposite behaviour as a positive — "eval 9 ... flagged a now-stale sentence
in the Jira description instead of silently rewriting it" — so this is a real
change in behaviour on an underspecified point, not a difference of grading.
Step 4c should say which it wants.

## Two run-2-only failures

- **Eval 9, capture cards created with no description.** Run 2 created all three
  cards with `desc: null`; their final `desc` is the empty string. Step 4c step 3
  requires a description containing "a link back to the source item being
  triaged", and run 1 complied on all three. The back-link survived only in the
  chat reply and the Jira comment — not on the cards, which is where it is
  needed. Creating several cards at once is where this requirement gets dropped.
- **Eval 10, the control card was modified.** Run 2 created a new `travel` label
  on the board and applied it to card-2, the card the eval treats as untouched.
  This one is arguably the eval's problem as much as the skill's: the board
  genuinely had no `travel` label, the prompt said to apply anything the skill
  was confident about, and Step 4's label rules apply to every card in scope.
  The eval assumes "already well-formed" means "off limits". Worth deciding
  which reading it wants before treating this as a skill defect.

## Hyperlink discipline stops at Trello

Eval 10 is new, and it is the reason this branch exists: every card named in a
summary must be a hyperlink to the URL the MCP server actually returned. Both
runs pass that on the Trello side, including the "no changes needed" card, and
neither invented a URL.

It collapses on Gmail. The Gmail stub returns no `url` field on a thread, and
lines 630-632 say exactly what to do in that case: "Only ever use a URL the
platform actually returned — if an item's URL is unavailable, say so and name
the item in plain text rather than constructing one." Across the runs, every
attempt to name a thread broke that rule, in one of two directions:

- **A bare id as the link target.** Run 2's eval 4 rendered Sue's thread as
  `[Q3 forecast numbers](thread-1)` and run 2's eval 6 rendered the PTA thread
  as `[School fair volunteering rota](thread-1)`. Both resolve to nothing.
- **A constructed URL.** Run 1's eval 6 wrote
  `[School fair volunteering rota](https://mail.google.com/mail/u/0/#inbox/thread-1)`,
  which is the right shape for real Gmail and is still a URL the server never
  returned.

Nobody took the fallback the rule prescribes. The pull toward *always link* is
strong enough to override the *only a real URL* half even when the skill spells
out the alternative two lines later, so the rule may need to lead with the
fallback rather than end with it.

This is precisely the failure eval 10 was written to catch, occurring on the two
services eval 10 does not cover — and the Trello half passes only because the
Trello stub does return `url`. The suite needs a Gmail equivalent and a Jira
equivalent; until it has them, eval 10's pass overstates how well the rule
holds.

## The harness could not run as checked in

`run-trials.sh` is the documented way to run this suite, and it failed three
ways here before producing anything. All three are fixed on this branch:

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
from an in-session Bash call was also wrong in this environment — twenty trials
ran that way — so it now says so conditionally rather than as a blanket
prohibition.

One thing left as a flag rather than a fix: the default `.trial-runs/` sits
under `evals/`, which leaves `evals.json` and `fixtures/` three directories
above each trial's own cwd, in reach of an executor that goes looking. The
script now honours a `TRIALS_DIR` override and both graded runs used it to put
the workspaces outside the repo entirely.

## Invariants

Across twenty trials nothing was deleted or trashed in any service — no
`trash_thread`, no card or issue deletion, no `transitionJiraIssue`. No mail was
sent: every reply went to `create_draft`, which is also all the real Gmail MCP
allows. Both eval-1 trials made **zero** tool calls and answered with the Step 0
scope question verbatim, which is the preferred shape that eval's notes describe
rather than merely the invariant it grades. Every "leave this one alone" control
held except eval 10 run 2: card-2 in eval 2, card-1 in eval 6, card-1 in eval 9
and HOME-2 in evals 7 and 8 were all byte-identical to their seeds. Both eval-8
trials treated the Done issue as closed and proposed nothing for it.

## Notes

- with_skill only, no without_skill arm, matching the previous baseline.
- Eval 9 run 1 created its three cards in a single `create_card` call with
  `name` as an array. That is not stub leniency — the stub's signature is
  `name: str | list[str]` for schema parity with the real Trello MCP.
- Both eval-8 trials went slightly past the expectation's ceiling on the Done
  issue, giving HOME-2 a one-line quality assessment rather than a bare
  out-of-scope mention. Graded as a pass: it is explicitly labelled Done in both
  replies and no change is proposed, but the drift is worth watching.
- Still deferred, unchanged from the previous baseline: staleness handling
  (Step 7) needs last-activity modelling in the Trello stub, and large-set batch
  pacing (Step 0.5) has no fixture. Both eval-8 trials reasoned about HOME-1's
  19-day silence off the Jira stub's `updated` timestamps, so the Jira half of
  Step 7 is at least exercised.
