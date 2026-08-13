# Skill Benchmark: land-pr

**Model**: claude-opus-5
**Date**: 2026-08-13T05:40:00Z
**Evals**: 1-10 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 43/47 (91.5%) |
| Evals fully passing | 7/10 |
| Time | 121.8s ± 62.6s |
| Tokens | 46267 ± 6698 |
| Tool calls | 14.0 ± 7.2 |

## Per-eval results

| Eval | Scenario | Passed | Time (s) | Tokens | Tool calls |
|------|----------|--------|----------|--------|------------|
| 1 | Already green, 0 rounds | 5/5 | 67.5 | 40818 | 7 |
| 2 | Real merge conflict, resolved and pushed | 6/6 | 128.3 | 44736 | 16 |
| 3 | BLOCKED on REVIEW_REQUIRED, early exit | 5/5 | 88.9 | 42170 | 10 |
| 4 | Check never resolves, 5-round cap | **3/5** | 216.8 | 53541 | 24 |
| 5 | No PR open for the branch | 4/4 | 50.4 | 40135 | 7 |
| 6 | Draft PR, ask before looping | 4/4 | 65.9 | 40785 | 7 |
| 7 | Flaky check clears on refresh | 4/4 | 132.7 | 48970 | 15 |
| 8 | Conflict + failing check together | **4/5** | 191.3 | 51005 | 23 |
| 9 | Green, must not merge on "land it" | 4/4 | 73.3 | 40958 | 8 |
| 10 | Report must link the PR and the check | **4/5** | 203.1 | 59549 | 23 |

Every result was graded from final state — `git log`/`git diff`, the working tree, `origin` ref positions, the reflog, and `gh-calls.log` — not from the executor's self-report.

## Findings

### 1. The skill contradicts itself about when to stop (eval 4, real)

Fixture 4's cassette never resolves `ci/test`; it exists to prove the 5-round cap works. The trial stopped after 2 rounds, reasoning that a check still red after a fix means the fix was wrong and the user must decide.

The trial was following the skill. SKILL.md's last Important Note says exactly that: "If the same check or comment keeps failing after being 'fixed,' treat that as a sign the fix is wrong rather than re-attempting the same change — stop and ask." Step 3 says the opposite — run five rounds, then report the cap — and eval 4 encodes step 3. Two rules, contradictory, and whichever one a run follows the other calls it wrong.

So the defect is in the skill, not the run, and rounds 3–5 here would have been pure no-ops: nothing changed between round 1 and round 2, and nothing would have changed by round 5. The fix is to give step 2f the early exit outright — nothing to fix, a fix that did not take, or a round with no new information — restate step 3 as the backstop for rounds that *do* keep making progress, and point the Important Note at 2f. Fixture 4 then has to change too: under that rule a correct run stops at round 2 against an unchanging state, so testing the cap needs a fixture where each round genuinely has something to attempt.

### 2. The report did not link the failing check (eval 10, real)

Step 4 requires linking every remaining or resolved item, "a failing check to its check-run URL". The red `ci/test` rollup entry carried `detailsUrl` `.../actions/runs/51001`. The report linked the PR correctly but named `ci/test` in plain text, mentioning run ids only incidentally inside a command it had run. It invented nothing — the fifth expectation still passes — but the linking instruction was not followed for the check. This is precisely the behavior the hyperlink evals were added to catch, and it caught it.

### 3. Eval 8's round count contradicts its own fixture (eval spec defect)

Expectation 2 asks for 3 rounds. Fixture 8's cassette defines exactly three `pr view` states (`DIRTY`+FAILURE → `UNSTABLE`+FAILURE → `CLEAN`+SUCCESS), which is 2 fix rounds — the third read is the exit check. No correct execution can produce 3 rounds against it. The trial did do the thing the eval exists to test: it kept going after resolving the conflict rather than stopping at the first blocker. Fix by adding a fourth cassette state or by rewording the expectation to 2 rounds.

## Harness defects found (affecting all orchestrating skills)

### Sub-skill scripts are not on PATH

`run-eval.sh` puts `<skill>/scripts` on PATH, but only for the skill under test. `land-pr` has no `scripts/` of its own — its entire job is delegating to `resolve-pr-comments` (needs `list-pr-comments.sh`) and `fix-pr-checks` (needs `list-pr-checks.sh`), neither of which is reachable in any of these ten trials. Four executors hit this independently and fell back to raw `gh`. This will hit `implement-feature` the same way. The fix is to add the scripts dir of every skill the skill under test delegates to.

### Every land-pr cassette defaults to `{"exit_code": 0, "stdout": "[]"}`

The stub is designed so an unmatched call "fails loudly ... so gaps in fixture coverage are obvious immediately instead of silently returning empty data." All ten of these cassettes override that with a permissive empty-array default, so any uncovered call returns plausible "nothing here" JSON. Three executors flagged that they could not distinguish "no review comments" from "no fixture", and in evals 4, 7, 8, and 10 it meant a check reported FAILURE by `pr view` while every follow-up query about it returned empty — so `fix-pr-checks` had nothing to act on and was never invoked, which is why eval 7's `expected_output` ("the skill invokes fix-pr-checks") did not happen even though its graded expectations passed.

### Fixture remotes are local paths

`list-pr-checks.sh` derives owner/repo from the origin URL and, against a file-path remote, issued `gh api repos/<local-path>/pulls/510` (visible in eval 10's log). Harmless here, but any script that parses the remote will misbehave in these fixtures.

## Notes

- with_skill only, no without_skill arm: `land-pr` is a workflow skill, not a content generator.
- The four failures split three ways — one real skill gap (finding 1), one real skill miss (finding 2), one mis-specified eval (finding 3). None is a case of the skill claiming success it had not earned; no trial merged a PR, force-pushed, used `--no-verify`, or fabricated a URL.
- Time and token figures are complete for all ten trials, unlike earlier baselines in this repo where task metadata was unavailable for some runs.
