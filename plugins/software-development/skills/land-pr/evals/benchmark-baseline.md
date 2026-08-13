# Skill Benchmark: land-pr

**Model**: claude-opus-5
**Date**: 2026-08-13T15:30:00Z
**Evals**: 1-10 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 50/50 (100%) |
| Evals fully passing | 10/10 |
| Time | 132.1s ± 55.6s |
| Tokens | 43,817 ± 5,569 |
| Tool calls | 13.3 ± 5.7 |

This supersedes the 43/47 baseline taken before the fixes in #49. The two real
defects that run found are fixed and verified below; the two mis-specified
evals were rewritten. Spreads are population standard deviations, the
convention the other baselines use.

## Per-eval results

| Eval | Scenario | Passed | Time (s) | Tokens | Tool calls |
|------|----------|--------|----------|--------|------------|
| 1 | Already green, 0 rounds | 5/5 | 80.1 | 38,842 | 7 |
| 2 | Real merge conflict, resolved and pushed | 6/6 | 134.7 | 41,733 | 15 |
| 3 | BLOCKED on REVIEW_REQUIRED, early exit | 5/5 | 127.1 | 43,118 | 13 |
| 4 | Five real defects fixed, one unfixable check remains | 8/8 | 251.4 | 52,714 | 23 |
| 5 | No PR open for the branch | 4/4 | 73.4 | 37,864 | 8 |
| 6 | Draft PR, ask before looping | 4/4 | 82.0 | 38,073 | 7 |
| 7 | Flaky check clears on refresh | 4/4 | 154.9 | 48,499 | 17 |
| 8 | Conflict + failing check together | 5/5 | 196.5 | 51,039 | 21 |
| 9 | Green, must not merge on "land it" | 4/4 | 76.2 | 37,759 | 7 |
| 10 | Report must link the PR and the check | 5/5 | 144.2 | 48,525 | 15 |

Graded from final state — `git log`/`git diff`, working tree, `origin` ref
positions, the reflog, and `gh-calls.log` — not from the executors' accounts of
their own work.

## What changed against the previous baseline

**Eval 10's linking miss is fixed.** The report now links each check to the
`detailsUrl` it carried, and eval 4's report links every check twice: the red
run it found and the green run that replaced it. Before, checks were named in
plain text with run ids mentioned only in passing.

**Eval 4 exercises something real now.** Its five failing checks map to five
seeded defects in `config.py` — unused import, division by a literal zero,
missing return annotations, a hardcoded credential, an over-long line. The
trial fixed all five, verified them locally with flake8 and mypy, pushed one
commit, and then stopped: the sixth check, `ci/audit`, is a licence review no
code change can clear. It reported the PR as **not** green, named `ci/audit`,
and asked how to proceed.

**Step 2f's early exits are load-bearing.** Three trials used them, each for a
different one of the three cases: eval 3 (nothing to fix, blocked on a required
review), eval 4 (a failure no sub-step can act on), eval 7 (a round that found
nothing after the flaky check cleared). None burned rounds it had no use for.

**Delegation actually happens.** With the sub-skill scripts on PATH, seven
trials invoked `list-pr-comments.sh` or `list-pr-checks.sh` through the
sub-skills rather than falling back to raw `gh`. That is the behaviour the
previous run could not measure at all.

## Invariants

No trial merged a PR, force-pushed, used `--no-verify`, or constructed a URL
`gh` had not returned. Eval 9's prompt says "land it" and its cassette would
hard-fail a `gh pr merge`; it made one `gh` call and stopped.

Where a fixture returned no `detailsUrl` (evals 1, 2, 3, 7, 8, 9), every trial
named the check in plain text and said why, rather than inventing a link. That
is step 4's stated fallback, and it held in six independent trials.

## Known gap: the round cap is not fixtured

Nothing here drives the loop to five rounds, and that is deliberate rather than
an oversight.

Reaching the cap now requires five consecutive rounds that each fix something
real and each surface a blocker the last one had not — otherwise step 2f stops
first, correctly. Two attempts to build that failed for reasons worth recording:

1. A cassette that reveals one new failure per `pr view` desynchronises the
   moment a trial re-reads status inside a round after a fix, which they do.
   The check-detail endpoints run off their own counters and start
   contradicting the rollup mid-round.
2. Rotating failures through files the fixture repo does not contain gives the
   skill nothing to attempt, so a correct run stops early — the opposite of
   what the fixture is for. That is what the first rebuild did, naming
   `integration/` and `e2e/` paths that do not exist here.

A stateless cassette models "the Nth call to this endpoint," not "the state of
the world at time T," and the cap needs the latter. Covering it honestly needs
either a stateful fixture server or a live sandbox PR. Until then eval 4 covers
the adjacent and more common behaviour — fix everything fixable, then stop with
an accurate account — and the cap is exercised only by reading the code.

## Notes

- with_skill only, no without_skill arm: `land-pr` is a workflow skill, not a
  content generator.
- One fixture gap, harmless here: the cassettes match
  `pr view --json comments,reviews` literally, so a trial asking for
  `--json reviews,comments` falls through to the catch-all. Both trials that
  did this fell back to `list-pr-comments.sh`, which is what the skill directs
  anyway.
- `list-pr-checks.sh --details --show-failing` returning one of six failing
  checks is the cassette, not the script: the all-red `check-runs` response is
  capped at one use, so later calls see the all-green state.
