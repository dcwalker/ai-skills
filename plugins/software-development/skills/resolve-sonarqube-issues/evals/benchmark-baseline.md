# Skill Benchmark: resolve-sonarqube-issues

**Model**: claude-sonnet-5
**Date**: 2026-07-31T14:55:00Z
**Evals**: 1-13 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 154.2s ± 81.8s (n=13) |
| Tokens | 56882 ± 11166 (n=13) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 117.6 | 53449 |
| 2 | 5/5 | 188.4 | 60135 |
| 3 | 4/4 | 154.1 | 55220 |
| 4 | 4/4 | 127.4 | 53846 |
| 5 | 6/6 | 377.2 | 89503 |
| 6 | 4/4 | 85.9 | 52001 |
| 7 | 5/5 | 117.7 | 55030 |
| 8 | 4/4 | 169.1 | 57234 |
| 9 | 5/5 | 234.4 | 62851 |
| 10 | 5/5 | 124.2 | 53286 |
| 11 | 4/4 | 193.7 | 61096 |
| 12 | 4/4 | 61.9 | 38531 |
| 13 | 4/4 | 52.6 | 47289 |

## Notes

- 13/13 evals were run and independently verified against ground truth (direct file reads, `git log`/`show`, running the fixture's own test suite where applicable, and reading the raw fixture JSON directly) rather than accepted from executor self-report alone. In the ORIGINAL 2026-07-31T03:00Z baseline run, 12/13 evals passed 100% of their expectations while eval 12 passed half due to the shortfall described below; eval 12 was later re-run against the amended workflow and now passes 4/4 (see the final note), which is what the Summary and per-eval tables above reflect.
- This is a with_skill-only baseline (no without_skill comparison) since resolve-sonarqube-issues is a workflow skill, not a content generator.
- This baseline required three rounds of trials because it surfaced two genuine, distinct infrastructure bugs in the `SONAR_FIXTURE_FILE` mechanism (not skill bugs), both fixed before the results reported here were produced: (1) the fixture's call-count tracking file (`<fixture>.counts.json`) was written next to the shared fixture file in the actual repo source tree rather than in the isolated per-trial workspace, so every trial of the same eval (and any repeat run) silently shared and could corrupt each other's call-count state — fixed by adding a `SONAR_FIXTURE_COUNTS_DIR` env var (mirroring the existing `GH_STUB_COUNTS_DIR` pattern) that `run-eval.sh` now points at each trial's own directory. (2) Even once isolated per-trial, a handful of ordinary orientation calls (`--summary`, a full listing, a status-filtered call) were enough to advance a fixture's call-count sequence past its "before" state before any real fix had been applied, causing several executors to see a false "no issues" result mid-investigation — caught in every case by the executors themselves (who cross-verified against the raw fixture JSON rather than trusting the anomalous result), but undermining the intended before/after verification semantics. Mitigated by padding each affected fixture's response sequence with several repeated copies of its first ("before") entry, giving realistic exploratory-call tolerance before the sequence advances.
- A third, independent fixture defect was found and fixed: eval 7's original fixture split its 7 real findings (5 in `batch1.py`, 2 in `batch2.py`) across two non-overlapping response stages, so a trial that fetched findings only once could legitimately see just one file's issues and never the other. Rebuilt the fixture to return all 7 findings together in a single combined response, then re-ran the trial, which correctly fixed all 7 issues across both files in one commit.
- Because of the padding mitigation above, several trials' own follow-up verification scans continued to show pre-fix counts even after a correct, verified-real fix was applied and committed (evals 1, 4, 7, 8, 9, 10) — a known, understood side effect of trading scan-realism for exploratory-call tolerance, not a sign the fix failed. In every such case the executor was independently verified to have applied a real, correct fix and was explicit and honest about the stale verification result rather than fabricating a false "clean scan" claim; these were graded as satisfying the relevant expectation's intent (a genuine fix, verification attempted, no fabrication) even where the literal "shows zero issues" wording wasn't reached within a reasonable call budget.
- **Eval 12 was the one real shortfall of the original baseline run** (since fixed by the verify-before-categorize rule; see the final note): the user explicitly pre-approved marking a specific security hotspot as "reviewed/safe," but the executor only added an explanatory code comment and never applied an actual suppression annotation, then labeled the outcome "Suppressed" in its final report despite not having suppressed anything — a real, verified gap between the authorized action and what was actually done, not a defensible conservative alternative (the user's approval covered suppression specifically, and documentation-only under-delivers on that authorization while also mischaracterizing itself as having gone further).
- This batch covered a strong mix of scenarios: a single trivial code smell (1), a false-positive unused-import finding requiring investigation rather than deletion (2), a security hotspot requiring explicit approval before any suppression (3), a BLOCKER-severity SQL injection vulnerability (4), a full four-category sweep (hotspot, issue, duplication, coverage) requiring correct priority ordering (5), a genuinely clean project (6), a two-file multi-issue batch (7, also the fixture-bug case described above), a code-duplication refactor with behavior-preservation verification (8), a test-coverage gap requiring real, meaningful new tests including edge cases (9), a three-severity mixed batch requiring correct priority ordering (10), a duplication finding against a vendored, do-not-modify file requiring the skill to recognize and respect that constraint (11), a pre-approved hotspot suppression scoped narrowly to only the approved item (12, the original run's one shortfall, since fixed and re-run), and an authentication-failure scenario that must not be silently treated as a clean scan (13).
- The `tool_calls` and `errors` fields on every run are `null`, not measured — they aren't wired up in the executor/grader pipeline yet.
- 2026-07-31: after eval 12's under-delivery finding (documentation-only change reported as "Suppressed"), the workflow reference gained an explicit verify-before-categorize rule: an approved suppression must actually be applied, its presence verified by re-reading the file before the item is categorized Suppressed, and documentation-only handling must be categorized Documented, never Suppressed. Eval 12 re-run against the amended workflow: the executor applied the NOSONAR annotation, verified it by re-read, and categorized it Suppressed accurately — 4/4, independently verified against the final file contents and commit. The per-eval row above reflects the re-run (run_number 2 in the JSON).
