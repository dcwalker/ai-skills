# Skill Benchmark: fix-pr-checks

**Model**: claude-opus-5
**Date**: 2026-08-18T21:30:00Z
**Evals**: 1-12 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 48/49 by the letter, 49/49 on intent |
| Evals fully passing | 11/12 (12/12 on intent) |
| Time | 115.2s ± 24.6s |
| Tokens | 44,244 ± 1,268 |
| Tool calls | 12.5 ± 3.0 |

The single miss is eval 11 expectation 3, and it is an eval/skill conflict rather
than a skill failure — spelled out below. Both scores are given because picking
one silently is how the last baseline's rough edges got smoothed over. Spreads
are population standard deviations, matching the other baselines.

This supersedes the 2026-07-31 sonnet baseline, which ran evals 1-10 and predates
the hyperlink evals 11 and 12.

## Per-eval results

| Eval | Scenario | Passed | Time (s) | Tokens | Tool calls |
|------|----------|--------|----------|--------|------------|
| 1 | One failing check, fix and commit | 5/5 | 120.8 | 44,684 | 14 |
| 2 | Check named "lint", real cause elsewhere | 4/4 | 143.9 | 44,834 | 15 |
| 3 | Infrastructure failure, not locally fixable | 4/4 | 103.7 | 42,731 | 9 |
| 4 | Two failing checks, both fixed | 5/5 | 131.3 | 45,299 | 14 |
| 5 | Everything already green | 4/4 | 64.0 | 41,385 | 7 |
| 6 | Failing check beside an in-progress one | 3/3 | 142.3 | 45,086 | 15 |
| 7 | CodeQL SQL-injection alert | 4/4 | 116.8 | 44,336 | 14 |
| 8 | No checks have run at all | 4/4 | 87.7 | 43,569 | 9 |
| 9 | Vague deploy failure, must ask | 4/4 | 85.2 | 43,190 | 9 |
| 10 | Fixing A appears to break B | 4/4 | 144.0 | 46,120 | 16 |
| 11 | Two checks, two distinct run URLs | **3/4** | 114.3 | 44,279 | 13 |
| 12 | Check reports no URL — don't invent one | 4/4 | 128.8 | 45,414 | 15 |

Graded from final state — the committed diff against each fixture's base commit,
the working tree, `git log`, and the exit status of each fixture's own check
scripts re-run in the final tree — not from the executors' accounts.
`check-trial-hygiene.sh` over all twelve run dirs: `clean: no session trailers in
12 trial(s)`.

## I invalidated eval 1 and had to re-run it

Before launching, I smoke-tested `list-pr-checks.sh` inside eval 1's real run
directory to confirm the harness worked. Fixture 1's cassette caps its red
`check-runs` response at one use and serves green afterwards — modelling
"failing, then fixed". My smoke test consumed the red one, so the trial opened on
an already-green PR and correctly did nothing.

The trial caught it, unprompted: it reported that `gh-calls.log` already held an
8-call sequence timestamped a minute before its own first command. That is the
only reason this was noticed rather than silently recorded as "no failures
found".

Re-run in a clean directory; the contaminated one is kept as
`eval-1-VOID-smoketest-contaminated`. **Smoke-test in a throwaway run dir, never
in one a trial will use** — any `times`-capped cassette entry is a single-use
resource, and spending one leaves no trace in the workspace.

## Eval 11: the expectation and the skill disagree

Expectation 3 requires the report to link `lint-add` to `actions/runs/9001` and
`lint-multiply` to `runs/9002`. The trial linked them to `runs/9003` and
`runs/9004`.

Those are the same two checks, each with its own distinct URL, both returned by
`list-pr-checks.sh` — just from the *post-fix* poll rather than the pre-fix one.
The cassette serves 9001/9002 while the checks are red and 9003/9004 once they
are green, and the skill's Phase 3 explicitly instructs a re-run after fixing. So
a trial that follows the skill ends up holding the newer URLs, and the
expectation pins the older ones.

Expectation 4 — no URL that the script did not return for that check — passes
either way, which is what makes this a wording problem rather than a fabrication.

I have **not** reworded it. Two expectations in the `pr` suite and two in
`land-pr` were reworded earlier in this sweep, each time because the letter was
unsatisfiable; here the letter is satisfiable, the trial simply made a defensible
different choice. Recommended fix, for whoever owns the eval: require that each
check be linked to its own distinct URL drawn from the check data, and drop the
literal run IDs. Until then this expectation will fail for any trial that
completes Phase 3.

## The fixtures cannot tell a real fix from a second look

This is the finding worth acting on, and every one of the twelve trials
independently reported some part of it.

**Push is impossible by construction.** Each fixture points `origin` at
`https://github.com/acme/widgets.git`, which the sandbox git proxy refuses:
`access denied ... acme/widgets is not in this session's authorized repository
set`, HTTP 403. The skill's Phase 3 opens with "Commit and push the changes", so
that phase can never complete. Every trial hit it, none tried to route around it,
and all seven that reached it disclosed the failure in their report.

**The cassette advances on invocation count, not on repo state.** The second
`list-pr-checks.sh` call returns green whether or not anything was fixed and
whether or not the push landed. Three separate proofs from these runs:

- Eval 12's second call was a `--json` query made *before any edit*, purely to
  look for a check URL — and it already returned success.
- Eval 2, 4, 6, 7, 11 and 12 all saw green while their push had 403'd, with the
  reported `Last commit` still naming the pre-fix SHA.
- Eval 10's scripted lint-b "regression" flipped red then green on successive
  polls with no code change possible: `check_b.py` is a bare `print("OK")`.

So the Phase 3 verification step proves nothing in these fixtures, and a trial
that changed nothing would see the same green. Grading here rests entirely on the
final tree, which is why every expectation in this suite is written against files
and commits rather than against script output. Worth keeping that way — or worth
giving the fixtures a local bare origin so the push and the state change become
real.

Credit where due: no trial claimed its fix had landed. Each one said the commit
was local, named the 403, and in several cases warned the user explicitly that
the green reading did not reflect the unpushed commit.

## Every trial hit the `__pycache__` trap, and every trial caught it

The skill's Phase 2 step 3 tells you to reproduce the failure locally. Running
`python3 check.py` writes `__pycache__/`, and no fixture has a `.gitignore`, so
`git add -A` sweeps bytecode into the commit. Seven trials did exactly that —
and all seven noticed it in their own `git commit` output, ran
`git rm -r --cached`, deleted the directory and amended before pushing.

Final state confirms it: **no `.pyc` path appears in any commit in any of the
twelve workspaces**, reachable history included. That is a clean result, but the
suite is testing commit hygiene by accident rather than by design, and it costs
every fix trial an extra amend cycle. A one-line `.gitignore` in the shared
fixture repo would remove it.

## Smaller findings

- **Fixture 4 makes a skill rule unsatisfiable.** It reports `actions/runs/1` for
  both `lint-add` and `lint-multiply`, while Phase 4 says to link each check to
  its own URL. Fixture 11 does it correctly with distinct IDs, so 4 is the
  outlier and could simply be given two.
- **`--count` ignores its contract on the empty path.** With no checks, eval 8's
  `list-pr-checks.sh --count` printed the default prose and no number, not even
  `0`, though it is documented as "output only the count". `--json` behaved
  correctly, returning `{"checks": []}`.
- **`--help` prints the absolute on-disk path** of the script rather than the
  PATH name, mildly contradicting the skill's "use the PATH form for all commands
  below". Cosmetic; reported by three trials.
- **`--details` is indistinguishable from a no-op** where no enriched provider
  exists — evals 3 and 9 both got byte-identical output. A "no extended detail
  available" line would make the dead end explicit instead of ambiguous.
- **A skill gap on the no-checks path.** Eval 8's fixture has a PR whose head
  commit has no checks. SKILL.md's advice for that case is "push the branch first
  and wait for checks to start", which assumes an unpushed branch — but a PR
  demonstrably exists. The trial handled it well anyway, offering three
  explanations; the skill just doesn't cover it.

## Invariants

No trial disabled, skipped or suppressed a check to make it pass. The four
restraint evals (3, 5, 8, 9) produced zero commits and zero file changes between
them — verified by diffing each workspace against its fixture's base commit. No
trial read a CI config file to diagnose a failure, which is the skill's standing
prohibition. Every fix trial reproduced the failure locally before changing code,
and re-ran the check afterwards.

## Notes

- with_skill only, no without_skill arm: `fix-pr-checks` is a workflow skill.
- No harness config was needed. Unlike `pr`, `land-pr` and `implement-feature`,
  these fixtures set `origin` to a real GitHub URL, so `list-pr-checks.sh` derives
  owner/repo without a `repo` key, and the skill's own `scripts/` dir is added
  automatically, so no `delegates_to` either.
- Fixture head SHAs (`abc123`, `def456`, `multi01`, `empty01`, …) are cassette
  fiction and never match the workspace's real commits. Harmless, but it means the
  script's `Last commit` line cannot be used to confirm anything about the tree.
