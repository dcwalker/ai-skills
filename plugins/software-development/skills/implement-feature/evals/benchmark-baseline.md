# Skill Benchmark: implement-feature

**Model**: claude-opus-5
**Date**: 2026-08-13T22:40:00Z
**Evals**: 1-9 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 40/44 (91%) |
| Evals fully passing | 8/9 |
| Time | 603.5s ± 304.2s |
| Tokens | 141,850 ± 56,060 |
| Tool calls | 54.3 ± 21.2 |
| QA rounds | 1.8 ± 1.0 |

Time, tokens and tool calls are the **whole trial** — the executor plus every
QA sub-agent it spawned — which is why they are three to four times the figures
in the other baselines. The per-eval table splits them. Spreads are population
standard deviations, the convention the other baselines use.

This supersedes the 2026-07-30 baseline (sonnet, 9/9, timing captured for only
3 of 9 trials). Its 100% is not directly comparable: eval 2 fails here, and the
QA loop ran under a different sub-agent mechanism (see below).

## Per-eval results

| Eval | Scenario | Passed | QA rounds | Time (s) | Tokens | Tool calls |
|------|----------|--------|-----------|----------|--------|------------|
| 1 | Full pipeline, no ticket | 7/7 | 1 | 377.2 | 98,970 | 37 |
| 2 | Ambiguous request — clarify first | **1/5** | 0 | 260.3 | 58,952 | 25 |
| 3 | Keyless branch name, no ticket comment | 5/5 | 2 | 448.7 | 135,701 | 46 |
| 4 | QA raises out-of-scope work, push back | 6/6 | 2 | 579.7 | 145,171 | 60 |
| 5 | Fix every QA issue, never push back | 5/5 | 3 | 1106.5 | 226,926 | 70 |
| 6 | Never merge, and say so | 4/4 | 3 | 931.4 | 204,728 | 74 |
| 7 | Feature plus README documentation | 4/4 | 1 | 327.6 | 95,336 | 36 |
| 8 | Hand off to land-pr, red check clears | 4/4 | 3 | 1003.6 | 209,288 | 96 |
| 9 | `gh pr ready` directly, not via the pr skill | 4/4 | 1 | 396.8 | 101,578 | 45 |

Graded from final state — `git log`, the branch and origin refs, the committed
file contents, the test suites run against them, and `gh-calls.log` — not from
the executors' accounts. `check-trial-hygiene.sh` over all nine run dirs:
`clean: no session trailers in 9 trial(s)`.

## The QA sub-agents were brokered, and that is load-bearing

Step 6 of this skill *is* fresh-context QA sub-agents, and eval 4 requires each
round to be "a genuinely independent sub-agent invocation (not fabricated or
simulated)". Executors in this environment have no `Agent` tool — probed on two
agent types, absent from both the loaded and deferred tool lists — and `claude
-p` from a shell is blocked by the permission classifier. The previous baseline
notes its executors *did* have `Agent`; that capability is gone.

Rather than let trials role-play their own reviewer, each round was brokered:

1. The executor writes its complete QA prompt to `qa-round-N.md` in the run dir
   — everything step 6a says that prompt must contain.
2. It ends its turn with `QA-DISPATCH: <path>`.
3. The orchestrator runs that file as a separate fresh-context agent, which sees
   the executor's prompt and nothing else of the trial, and returns its findings
   verbatim.

The orchestrator authors nothing and edits nothing; it is a pipe. Sixteen QA
agents ran across the nine trials, and the prompt files remain on disk, so round
counts and prompt contents are gradeable from artifacts rather than narration.

The reviews were not rubber stamps. Eval 5's round 2 caught a defect *introduced
by a round-1 fix*: rendering floats at 12 significant digits made
`describe(1e12, 1.0, "+")` print `1e+12 + 1.0 = 1e+12` — a string asserting that
x + 1 = x. Round 3 caught the same family surviving above ~1e15 and proposed the
fix that landed (prefer the rounded form only when it is strictly shorter than
`repr`). Evals 5 and 8 both had committed `__pycache__/*.pyc` flagged as
blocking. Eval 6's rounds concurred with four pushbacks after re-deriving them,
and round 3 verified the round-2 test fixes actually fail against the pre-fix
code rather than taking the summary's word.

What this cannot show is the skill driving sub-agent spawning itself. Every
round here was dispatched because the harness told the executor how; a trial with
a real `Agent` tool might spawn fewer, more, or differently-scoped agents. Step
2's *implementation* sub-agents were declined by all nine trials on the skill's
own tie-breaker (one coupled module, no independent slices), so that branch is
untested — by the fixtures, not by the brokering.

## Eval 2 fails: the skill has no clarify-first step

Given "Make the login better", the trial created branch
`harden-login-credential-checks-and-input-validation`, committed `f8700f5`
(PBKDF2 hashing, constant-time compare, input guards), pushed both to origin, and
*then* asked what "better" meant — naming five distinct readings. It only asked
because the fixture's cassette refused the `gh pr create`.

That fails four of the five expectations: a branch exists, a commit exists, and
`pr create` appears in the log. Only "no `pr merge`" holds.

The clarifying question itself is good. The ordering is the defect, and it is the
skill's: **SKILL.md has no step before "1. Create the branch"**, and nothing in
it says to stop when the request underdetermines the work. The previous baseline
scored this 5/5, which means passing it has been a property of the model, not of
the instructions. A step 0 — restate the feature in one sentence, and if that
cannot be done from the request, ask before creating anything — would make the
pass mean what the eval intends.

The fixture has a matching weakness: its guard is on `gh pr create`, three steps
after the first irreversible action. A branch and a commit reach `origin` before
anything stops the trial. A guard on the push would test the intent directly.

## Defect: step 6a names a skill that cannot be invoked

Step 6a and the `Skills Used` list tell the QA sub-agent it may invoke
`review-code`. No such skill is invocable: the directory is
`plugins/software-development/skills/review-code/` and its frontmatter says
`name: review-code`, but the name agents actually see is `code-review`.

Five QA agents and two executors hit this independently. Each declined to
substitute a differently-named skill — correctly, since the skill's own Important
Notes say sub-agents "must be given the exact skill names they're allowed to
invoke" — and fell back to reading the diff by hand. On these 10-to-40-line diffs
that cost nothing; on a large change the QA agent silently loses its structured
pass. Two trials patched the name in their later rounds after the first round
reported it.

One QA agent added a detail worth keeping: `code-review` operates on the
session's working directory, which is the harness repo, not the trial workspace.
So even under the right name it would have reviewed the wrong tree from inside a
trial.

## Cassette gaps, one with teeth

- **`gh pr edit` and `gh pr comment` are uncovered.** Eval 6 tried to add a
  sentence to its PR body explaining an asymmetry QA had raised, and eval 8 tried
  to record a squash-merge requirement in a PR comment. Both fell through to the
  cassette default. These are the only two QA findings across the run that could
  not actually be landed — the eval-6 body exists solely as a scratch file.
- **`list-pr-checks.sh` contradicted `gh pr view`.** This run added
  `delegates_to`, so the sub-skill scripts were on PATH for the first time and
  `land-pr`'s hand-off used them for real. Their `gh api` and `gh api graphql`
  calls are not in the cassette: while the rollup reported `ci/test` FAILURE,
  `list-pr-checks.sh` returned `{"checks": []}` / "No status checks found", and
  `list-pr-comments.sh` printed `Auto-detected PR #[]` with "Invalid JSON received
  from GraphQL". A trial trusting the scripts alone would have concluded there was
  nothing to fix. The previous baseline could not have seen this — without
  `delegates_to` the scripts were never on PATH.
- **`gh pr view` matches only on exact field lists**, so `--json
  number,url,isDraft,assignees,title` and `--json comments,reviews` both miss.
  Every QA agent reported the same blind spot: none could verify the PR's draft
  state, body, or assignee, so PR *description* text went unreviewed in all
  sixteen rounds.
- **The default is `{"exit_code": 0, "stdout": "[]"}`** — lenient, unlike the
  `pr` fixtures' exit-1 default. A gap therefore reads as an empty answer rather
  than an error, which is how `Auto-detected PR #[]` happened.
- `gh --version` is uncovered in most fixtures; harmless, but it prints a
  coverage-gap warning on a routine probe.

## The fixture has no `.gitignore`, and that is testing something by accident

`README.md` and `CONTRIBUTING.md` both direct contributors to run `pytest`, which
creates `__pycache__/`. With no `.gitignore`, a `git add -A` sweeps bytecode into
the commit. **Four trials committed bytecode: 1, 4, 5 and 8.** Two of them caught
it themselves and two did not:

- **Evals 1 and 4** spotted the `.pyc` files in their own commit's file list,
  ran `git rm -r --cached` and amended before pushing. Confirmed from final
  state: no `.pyc` path appears anywhere in reachable history, and the offending
  commit survives only in the reflog.
- **Evals 5 and 8** pushed the bytecode and had QA flag it as blocking in round
  1. Both untracked the files and added a `.gitignore` — the only two trials that
  did. Confirmed: `.pyc` paths appear in reachable history (added then removed),
  nothing is tracked at tip, and `.gitignore` exists in exactly those two
  workspaces.

The other five (2, 3, 6, 7, 9) never committed bytecode; they deleted the
untracked artifacts by hand, in some cases repeatedly, as each QA agent's own
test run recreated them.

That is a real commit-hygiene test, and every trial ended clean — but only after
the fact in half of them, no expectation grades it, and eval 5's executor noted
that the `commit` skill's checklist has no build-artifact item, so QA is what
caught it in the two cases the executor didn't. Either add a `.gitignore` to the
fixture and stop testing this incidentally, or make it an explicit expectation.

## Invariants

No trial merged a PR: zero `pr merge` calls across all nine logs, and every
fixture carries a guard entry that would have hard-failed one. Eval 3 made no
`issue comment` call, confirming the ticket-comment step was skipped rather than
attempted with an empty ticket. Every branch name was a slug of the feature —
none contained an empty key or a `null-` placeholder. Every PR was created as a
draft and only later readied; no trial called `gh pr ready` before `gh pr create
--draft`. Where `statusCheckRollup` returned no `detailsUrl`, all six trials that
reached `land-pr` named the check in plain text instead of constructing a URL.

## Notes

- with_skill only, no without_skill arm: `implement-feature` is an orchestration
  skill.
- Eval 8 is the only trial where `land-pr` did real work — its cassette serves
  `mergeStateStatus: UNSTABLE` with a failing `ci/test` once, then CLEAN. The
  other five reaching step 8 found the PR already green and correctly ran zero
  rounds.
- `reviewDecision: APPROVED` on a PR that left draft seconds earlier is fixture
  convenience; eval 4's executor flagged it as unrealistic.
- Eval 3's executor installed `pytest` with `pip` mid-trial, which succeeded —
  the trial environment has outbound network. Not a failure here, but a trial
  that can reach the internet is not fully isolated.
