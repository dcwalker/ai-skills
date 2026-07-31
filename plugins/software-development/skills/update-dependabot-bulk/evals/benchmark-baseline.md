# Skill Benchmark: update-dependabot-bulk

**Model**: claude-sonnet-5
**Date**: 2026-07-31T00:10:00Z
**Evals**: 1-12 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 191.9s ± 154.1s (n=12) |
| Tokens | 59153 ± 15136 (n=12) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 4/4 | 158.3 | 59442 |
| 2 | 4/4 | 522.1 | 93232 |
| 3 | 4/4 | 144.9 | 54596 |
| 4 | 3/3 | 65.4 | 46834 |
| 5 | 4/4 | 60.1 | 47534 |
| 6 | 5/5 | 507.1 | 88481 |
| 7 | 4/4 | 108.2 | 51403 |
| 8 | 4/4 | 159.5 | 55619 |
| 9 | 3/3 | 208.0 | 57539 |
| 10 | 3/3 | 209.0 | 58939 |
| 11 | 4/4 | 135.8 | 55212 |
| 12 | 4/4 | 24.4 | 41001 |

## Notes

- 12/12 evals pass 100% of their expectations in this baseline run. All results were independently verified against ground truth (direct file reads, git log/show, and gh-calls.log contents) rather than accepted from executor self-report alone.
- This is a with_skill-only baseline (no without_skill comparison) since update-dependabot-bulk is a workflow skill, not a content generator.
- This baseline required three rounds of trials because it surfaced three genuine, distinct infrastructure/fixture bugs (not skill bugs), all fixed before the results reported here were produced: (1) the shared eval harness (`evals/lib/run-eval.sh`) never put a skill's own bundled `scripts/` directory on `PATH` for subagent executor trials — only the gh-stub was added — so `list-dependabot-prs.sh` could not be found; fixed by having `run-eval.sh` always prepend the skill's `scripts/` dir alongside the gh-stub, mirroring how a real Claude Code session exposes an active skill's bundled scripts. (2) Several `package-lock.json` fixtures (evals 1, 3, 4, 5, 8, 9, 10, 11, 12) shipped with fabricated all-zero placeholder integrity hashes, which made a real `npm install` fail with `EINTEGRITY` on every package in the file, not just the ones being bumped — forcing every npm-based trial through an unplanned lockfile-repair side-quest whose outcome varied by which workaround each executor happened to choose, rather than testing the skill's actual intended behavior. Fixed by regenerating all affected `package-lock.json` fixtures from the real npm registry. (3) Eval 11's fixture proposed bumping react to a fabricated version (18.2.9) that does not exist on the real npm registry (confirmed via `npm info react@18.2.9` → 404); fixed by retargeting the fixture and evals.json to a real published version (18.3.1).
- A fourth issue was fixture-narrative rather than infrastructure: evals 2 and 6 originally assumed that bumping eslint from 9.24.0 to 10.0.3 would pull `flatted` forward to >=3.4.0 via `file-entry-cache`/`flat-cache`. Verified directly against the live npm registry that this is false — every current eslint release (9.x through the actual latest, 10.8.0) still depends on `file-entry-cache@^8.0.0`, whose only release depends on `flat-cache@^4.0.0`, which only ever requires `flatted@^3.2.9`. `flatted`'s existing locked range already permits the target version, so it resolves via a plain lockfile refresh, independent of the eslint decision. Two independent executor trials of eval 2 discovered this same fact through real research and correctly declined to fabricate the assumed link. `evals.json` was corrected to grade the real, verified resolution path instead of the originally-imagined one. Eval 6's `expected_output` also had an internal inconsistency fixed at the same time: the prompt itself says to flag major-version items separately, but the original expectations bundled the eslint major bump into the auto-applied "safe" batch alongside patch-level lodash/chalk — corrected so both major bumps (eslint and axios) are expected to be flagged, not just axios.
- Eval 2's grading was written to accept two valid outcomes given its more ambiguous prompt wording (unlike evals 3 and 6, it doesn't explicitly say "flag risky items separately"): either applying the safe, independently-resolvable flatted fix while flagging eslint, or pausing to ask before touching anything once a major-version item was discovered mid-plan. Two independent trials both chose the latter, cautious path after doing the real verification work — treated here as a legitimate outcome, not a shortfall, consistent with the guide's principle of not rejecting valid alternative approaches.
- This batch covered a strong mix of scenarios: a clean two-PR direct-dependency batch (1), a transitive dependency requiring real npm/yarn research where the assumed resolution path turned out not to exist (2), a safe-plus-major mix (3), zero open PRs (4), a plan-only request with no pre-approval (5), a five-PR mix of safe/transitive/two-major items (6), an unresolvable transitive dependency via a fictitious parent package (7), a stale/already-satisfied PR alongside a real one (8), a single-PR bulk update (9), two PRs targeting the same package at conflicting versions (10), a monorepo with two package.json files (11), and a status-only request that must not build or push a plan (12).
- The `tool_calls` and `errors` fields on every run are `null`, not measured — they aren't wired up in the executor/grader pipeline yet.
- Unlike several earlier baselines this session, real time/token usage data was available for all 12 runs (via the background Agent tool's usage reporting), so no runs are missing from the aggregate time/token statistics.
