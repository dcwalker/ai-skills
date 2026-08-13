# Skill Benchmark: pr

**Model**: claude-opus-5
**Date**: 2026-08-13T21:40:00Z
**Evals**: 1-15 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 47/47 (100%) |
| Evals fully passing | 15/15 |
| Time | 92.3s ± 16.2s |
| Tokens | 39,074 ± 1,398 |
| Tool calls | 10.3 ± 1.5 |

This supersedes the 2026-07-30 baseline, which covered evals 1-14 under
claude-sonnet-5 and predates eval 15 (the hyperlink eval added in c0a7ac4).
Spreads are population standard deviations, the convention the other baselines
use. Time is the trial's wall clock; tokens are the final turn's context plus
that turn's output; tool calls are counted from the trial transcript.

## Per-eval results

| Eval | Scenario | Passed | Time (s) | Tokens | Tool calls |
|------|----------|--------|----------|--------|------------|
| 1 | Create: draft, links #42 | 6/6 | 91.1 | 39,665 | 10 |
| 2 | Update an existing PR, don't recreate it | 3/3 | 101.4 | 39,320 | 11 |
| 3 | Vague prompt, title must still be specific | 3/3 | 87.2 | 38,256 | 10 |
| 4 | Short PR template, used as the body's base | 3/3 | 127.0 | 42,029 | 13 |
| 5 | Long PR template, summarized not pasted | 3/3 | 118.4 | 42,135 | 12 |
| 6 | Assignment pre-answered yes | 2/2 | 81.1 | 38,551 | 11 |
| 7 | Assignment pre-answered no | 2/2 | 84.0 | 38,740 | 10 |
| 8 | Draft → ready for review | 3/3 | 96.8 | 38,852 | 11 |
| 9 | Update description and add assignee | 3/3 | 110.8 | 39,997 | 12 |
| 10 | Stale title must not be renamed silently | 3/3 | 95.3 | 39,197 | 12 |
| 11 | Two linked issues, both hyperlinked | 3/3 | 86.1 | 38,917 | 9 |
| 12 | No issue exists — invent no Related section | 3/3 | 76.5 | 37,228 | 9 |
| 13 | Short change — no tl;dr, ≤3 bullets | 3/3 | 63.1 | 37,591 | 7 |
| 14 | Branch has nothing to submit | 2/2 | 88.0 | 37,705 | 9 |
| 15 | Closing message links the PR and the issue | 5/5 | 77.3 | 37,927 | 9 |

Graded from final state — `gh-calls.log`, the exact `--title`/`--body` values
the stub recorded, the workspace's git state, and the trial's closing message —
not from the executors' accounts of their own work. `check-trial-hygiene.sh`
over all 15 run dirs reported `clean: no session trailers in 15 trial(s)`; this
was its first use on a real run.

## Five expectations were reworded before grading

Evals 4, 5, 6 and 10 each carried an expectation phrased around interactive
ordering — "asking whether to use it, **before creating the PR**", "without
that question **appearing first** in the transcript". A single-shot executor
cannot satisfy those as written: it has no interactive user, so every question
the skill raises is surfaced in its report, after the action it governed. Worse,
the prompts for 4, 5 and 6 *pre-answer* the question ("Yes, please use the
repo's PR template", "Yes, assign it to me"), so a skill that re-asked would be
wrong.

All three trials did exactly the right thing: each named the question verbatim
("A PR template was found. Do you want to use it as the base for the
description?", "Should I assign this PR to you?") and recorded that the prompt
had already answered it. Eval 10's trial quoted the stale title, called it
stale, stated the question, and named the default it took.

Grading the letter would have blamed the skill for the harness; grading it
loosely and saying nothing is what the 2026-07-30 baseline did. So the five
expectations now ask for what is actually observable — that the question and
its resolution appear in the transcript, rather than the decision being made
silently. No trial was re-run: executors are barred from reading `evals.json`,
so amending an expectation cannot change what a trial did.

The cost is honest to state: those five expectations can no longer distinguish
"asked, then acted" from "acted, then explained". Proving the ordering needs a
multi-turn harness that can withhold the answer and observe the skill stopping
to ask. Eval 7 is the one place the ordering is still pinned by an artifact
rather than by narration — its prompt declines assignment, and the absence of
`--assignee` in the create call is checkable without reading any prose.

## The first iteration was discarded, and why

All 15 trials in the first run failed setup with
`error: Cannot determine remote HEAD`. Fourteen of the 15 `pr` fixtures build
their own bare origin with a plain `git init --bare`, which inherits the
**host's** `init.defaultBranch`. Unset here, so the origin came up with
`HEAD -> refs/heads/master` while the fixture only ever pushes `main`, and the
following `git remote set-head origin --auto` aborted the fixture under
`set -e`. The failure is total: `run-eval.sh` dies before writing `env.sh`, so
the trial is unrunnable rather than merely odd — and invisible on any machine
that happens to set `init.defaultBranch=main`.

The executors worked around it by hand, which is why iteration 1 was thrown
away rather than graded: 49-59k tokens per trial against 37-42k for the clean
run, all of it spent on the harness. The fix is central, in `git-fixture.sh`
(commit 8a61a3b), so the 25 affected fixtures across `pr` and `create-branch`
and every future fixture inherit the guarantee.

## Fixture and cassette gaps found

None of these changed a verdict; all are worth knowing before the next run.

- **`gh repo view` is uncovered** in fixtures 5 and 11. Both trials called it to
  resolve `nameWithOwner`; both got the unmatched default and carried on from
  the remote URL they already had.
- **`gh issue view` is uncovered for issues 130, 140 and 160** (fixtures 8, 9,
  11). Evals 8 and 9 are `pr edit` scenarios whose expectations do not turn on
  the issue, and fixture 11's two graded issues (10 and 20) *are* covered.
- **The stub is stateless, so a post-create `gh pr view` reports no PR.** Eight
  trials made that read-back call and got the fixture's "no pull requests found
  for branch" back, because the cassette's `pr view` entry describes the state
  *before* the create and is not use-capped. Every one noticed, said so, and
  reported the URL
  `gh pr create` had actually printed rather than treating the read-back as
  truth. Flagged rather than fixed: adding a post-create `pr view` entry would
  shadow the pre-create one, which several fixtures need to be an exit-1.
- **`origin` deliberately points at `https://github.com/example-org/demo-app.git`.**
  Each fixture builds a local bare origin, pushes to it, sets the remote head,
  then rewrites the URL so `gh` infers the right repo. The remote-tracking refs
  are therefore real while `git fetch`/`git ls-remote` cannot work. Eval 14's
  trial hit this and reported it as a possible bug; it is intentional, and the
  `pr` skill never needs the network, but the next person to see it should not
  "fix" it.

## The skill has no branch for "nothing to submit"

Eval 14 passes, and cleanly: the trial found HEAD equal to both `origin/main`
and `origin/HEAD`, a clean tree and an empty stash, made exactly one `gh` call,
created nothing, and reported why. But it got there on its own judgement —
SKILL.md's "Gather context" step says to run `git log origin/HEAD..HEAD` and
never says what to do when the output is empty. The eval is currently testing
the model, not the skill. Adding an explicit early exit to step 1 would make
the pass mean what the eval intends.

## Invariants

No trial created a PR it was asked to update, or updated one it was asked to
create: evals 2, 8, 9 and 10 produced zero `pr create` calls, and evals 1, 3-7
and 11-15 produced zero `pr edit` calls. Eval 8 was the only trial to run
`pr ready`, and no trial ran `pr convert-to-draft`. Every created PR was a
draft — `--draft` is present on all 10 create calls.

No trial invented a URL. Every issue link resolves to an issue the fixture
exposes, every PR link is the URL the cassette's `pr create` printed, and
eval 12 — whose fixture has no linked issue — omitted the `## Related` section
entirely rather than filling it.

## Notes

- with_skill only, no without_skill arm: `pr` is a workflow skill, not a content
  generator.
- Eval 3's trial ran `gh pr view --json assignees,isDraft` twice; both returned
  the fixture's exit-1 "no PR". Harmless, and the second call is the skill's own
  re-check before creating.
- Assignment defaults: 9 of the 10 create trials passed `--assignee @me`; only
  eval 7, whose prompt declines, omitted it. Eval 6's prompt answered yes; the
  other eight took "yes" as an unstated default with no interactive user to ask,
  and each said so in its report. That default is the executor's, not the
  skill's — SKILL.md says to ask and states no default. Worth deciding on
  deliberately: a skill that must ask has no defined behaviour when it cannot.
