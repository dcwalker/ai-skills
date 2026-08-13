# Skill Benchmark: commit

**Model**: claude-opus-5
**Date**: 2026-08-13T20:00:00Z
**Evals**: 1-13 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 45/45 (100%) |
| Evals fully passing | 13/13 |
| Time | 93.0s ± 18.4s |
| Tokens | 37,877 ± 1,368 |
| Tool calls | 9.5 ± 2.2 |

Spreads are population standard deviations, matching the other baselines.

## Per-eval results

| Eval | Scenario | Passed | Time (s) | Tokens | Tool calls |
|------|----------|--------|----------|--------|------------|
| 1 | Clean diff, Jira key from branch | 5/5 | 79.9 | 37,803 | 11 |
| 2 | GitHub issue number from branch | 4/4 | 96.3 | 37,571 | 10 |
| 3 | Debug `console.log` left in the diff | 3/3 | 111.7 | 39,924 | 11 |
| 4 | Two unrelated concerns in one diff | 3/3 | 108.7 | 38,989 | 9 |
| 5 | No derivable ticket key | 3/3 | 73.7 | 35,773 | 5 |
| 6 | Lint broken, user pre-authorised skipping | 4/4 | 77.2 | 37,199 | 9 |
| 7 | Lint passes, no WIP warranted | 4/4 | 86.1 | 36,949 | 8 |
| 8 | Nothing to commit | 2/2 | 47.7 | 34,985 | 5 |
| 9 | Pre-commit hook rejects, then retry | 4/4 | 109.7 | 38,697 | 12 |
| 10 | User-facing CLI flag, README stale | 3/3 | 98.6 | 39,071 | 11 |
| 11 | New endpoint, `openapi.yaml` stale | 3/3 | 104.0 | 38,464 | 11 |
| 12 | Commented-out dead code in the diff | 3/3 | 110.5 | 39,356 | 12 |
| 13 | Rename across three files, one concern | 4/4 | 105.3 | 37,624 | 10 |

Graded from final state — `git log`, the diff against each fixture's base commit,
the committed file contents, and working-tree cleanliness — not from the
executors' accounts. Two self-reports were checked against the harness and one
was wrong; see Notes.

## What the suite exercises well

The negative cases are the strongest part of this suite, and all four held. The
skill declined to commit when it should decline: eval 4 stopped on two unrelated
concerns and asked, eval 5 stopped rather than invent a ticket key for branch
`quick-fix`, eval 8 refused to create an empty commit on a clean tree, and evals
3 and 12 both caught planted artefacts (`console.log("HERE")`, a commented-out
`parseCsvLineOld` block) and removed them before staging rather than committing
them unremarked.

Eval 9 is the most demanding and passed cleanly: the pre-commit hook rejected the
first attempt over trailing whitespace, and the trial located the exact line,
fixed it, re-staged and retried — ending with **one** commit, and no `--no-verify`
anywhere in the run.

The WIP pair works as designed. Eval 6's fixture ships a `package.json` whose
lint script is literally `exit 1`; the trial ran it, recognised the failure as
pre-existing (it fails on a clean tree too), and marked the commit `WIP:` with the
diagnosis in the body, as the prompt pre-authorised. Eval 7's lint passes and the
trial correctly did *not* mark WIP.

## Findings

### 1. Step 2's checklist says what to report, not what to do (skill gap)

Eval 12's trial named this itself. Step 2 asks the agent to confirm and report
"No debug code — [Yes / No — describe]", but only the *changes-are-related* item
carries an explicit branch for a "No" answer ("ask whether to commit them
separately or together"). The other three say nothing about what a "No" obliges.

In practice both affected trials chose to fix and report (evals 3 and 12 removed
the artefacts), and the expectations allow either — "removed or the user was asked
first". So this cost nothing here. But the two behaviours are materially different
for a user, and which one they get is currently down to the agent. Worth deciding
in the skill: remove-and-report, or stop-and-ask.

Evals 10 and 11 sit in the same space from the other direction. Both expectations
permit "asks whether to update the docs first **or** clearly flags the gap", and
both trials went further than either — they flagged the gap *and* closed it,
committing the README and `openapi.yaml` updates alongside the code. Defensible,
and arguably the most useful outcome, but again unspecified.

### 2. The harness leaks the orchestrator's commit conventions into trials

Evals 7 and 13 produced commits carrying `Co-Authored-By: Claude ...` and
`Claude-Session: ...` trailers. Nothing in the `commit` skill or the fixtures asks
for those — they come from the *orchestrating* session's own git instructions,
which the executor subagents inherit.

It changed no result here, because no expectation in this suite asserts on trailer
content. It would corrupt one that did, and it makes the committed message not
purely a product of the skill under test. The fix belongs in the executor prompt
or the trial environment, not in this skill.

### 3. `gh` availability differed across trials

Some trials found the stub and got its refusal (`GH_STUB_CASSETTE is not set`,
exit 1); others reported `gh: command not found`. The cause is the executor's
shell resetting between calls, so `PATH` from `env.sh` does not persist unless
re-sourced every time. Both paths land on "work-item lookup unavailable", so no
result moved, but the environment is not identical across trials and that is worth
knowing before any eval depends on `gh` being reachable.

## Notes

- with_skill only, no without_skill arm: `commit` is a workflow skill.
- `commit`'s fixtures carry no `gh-cassette.json`, so the stub refuses by design.
  That is the correct fail-closed behaviour and every trial handled it as tool
  unavailability rather than a blocker.
- `acli` is genuinely absent from the image, so the Jira branch of step 3 is
  unreachable in every trial. Eight of the thirteen fixtures use Jira-style branch
  names, so the ticket-lookup path is effectively untested — the key is always
  derived from the branch instead. Covering it would need an `acli` stub.
- One executor reported the `gh` stub "exits 0 while printing its refusal to
  stdout". Checked directly: it exits 1 and writes to stderr. The self-report was
  wrong, which is the argument for grading from final state.
