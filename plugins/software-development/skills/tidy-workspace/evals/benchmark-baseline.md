# Skill Benchmark: tidy-workspace

**Model**: claude-sonnet-5 (executor) / claude-opus-5 (analyzer)
**Date**: 2026-09-11T03:20:10Z
**Evals**: 1-15 (1 recorded run each, 3 for eval 3, 5 for eval 6, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 92% ± 13% |
| Time | 171.4s ± 89.6s (n=21) |
| Tokens | 72749 ± 2319 (n=21) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 6/6 | 446.5 | 74793 |
| 2 | 6/6 | 207.5 | 73519 |
| 3 (run 1) | 4/4 | 192.4 | 74190 |
| 3 (run 2) | 4/4 | 147.0 | 71022 |
| 3 (run 3) | 4/4 | 126.5 | 71830 |
| 4 | 5/5 | 68.9 | 69529 |
| 5 | 4/4 | 55.0 | 68254 |
| 6 (run 1) | 3/4 | 203.0 | 73236 |
| 6 (run 2) | 3/4 | 141.0 | 73276 |
| 6 (run 3) | 3/4 | 312.6 | 74237 |
| 6 (run 4) | 3/4 | 167.2 | 73279 |
| 6 (run 5) | 3/4 | 250.9 | 73999 |
| 7 | 4/4 | 133.2 | 74940 |
| 8 | 4/4 | 89.3 | 70954 |
| 9 | 4/4 | 101.8 | 71353 |
| 10 | 4/4 | 182.2 | 72861 |
| 11 | 3/5 | 237.5 | 79382 |
| 12 | 4/4 | 88.3 | 71529 |
| 13 | 5/5 | 185.9 | 73450 |
| 14 | 4/4 | 149.5 | 70960 |
| 15 | 4/4 | 114.2 | 71138 |

## Notes

- 15 evals and 21 recorded runs pass 84/91 expectations as observed. All 7 failures come from the permission classifier the trials ran under, which denied `git push origin --delete` in every eval 6 run and `git stash drop` in eval 11; counting only skill behaviour, every recorded run passes every expectation. 13 of 15 evals pass every expectation in every recorded run.
- Each eval records every run on the newest SKILL.md version it was tested against, not the best run. Evals 4, 5, 7, 8, 9, and 12 come from round 2, before the step 3 plan-first sentence, the worktree clarification, and the protected-branch rewrite; none of their expectations depend on those changes. Evals 1, 2, 10, 11, 13, 14, and 15 come from round 3, which added the plan-first sentence. Eval 3 records three runs with the clarified worktree exclusion, and eval 6 records five runs on the merged SKILL.md.
- This baseline accompanies PR #70: cleanup of files the session created outside the repo (evals 13 and 14), resolving ticket keys in their own tracker instead of by number (eval 15), a corrected eval 10 fixture, presenting the plan before acting on advance approval, deleting a merged branch once its worktree is removed, and naming the branches the skill must never delete.
- Evals 13, 14, and 15 are new. Eval 10's fixture changed: its cassette now records `Closes #123` and closing issue references on PR #88, returns consistent issue data, and fails on unrecorded calls. Before the fix eval 10 scored 1/4 in three runs, including one on the previous SKILL.md, because a run had to guess that PROJ-123 meant issue #123; after it, 4/4 in all four runs.
- Eval 6: before the protected-branch rewrite, 3 of 6 runs deleted develop, including one on the previous SKILL.md, each labeling it "not protected" and never citing the name list. With the rewrite, 5 of 5 kept develop and named it in the plan. Remote results cannot be confirmed in this permission mode; a mode that allows `git push origin --delete` should see eval 6 at 4/4.
- Eval 3: with the plan-first sentence but before the worktree clarification, 1 of 3 runs removed the stale worktree and then kept its merged branch; all 3 runs with the clarification deleted it.
- Plan ordering: with only the executor-prompt plan-first clause, 3 of 15 pre-approved runs changed something before showing a plan; with the SKILL.md step 3 sentence as well, 19 of 19 showed the plan first.
- Trials ran as Agent-tool Sonnet subagents in workspaces outside the repository, with the three clauses in evals/README.md's "What an executor must be told". Eval 6 runs were also told to report a denied command as blocked rather than reword it; earlier rounds without that instruction saw executors reword around denials, which affected no recorded run's expectations. check-trial-hygiene.sh found no session trailers in the 49 trials it covered (rounds 1 to 3, before the recorded eval 3 runs); evals 3 and 6 make no commits.
- Results were verified against ground truth: final git state (branches, remotes, worktrees, stashes), file checksums for evals 13 and 14, and gh-calls.log. Plan and report expectations were graded from executor output, and ordering expectations from the transcripts.
- Time and tokens come from each executor's Agent tool completion report (wall-clock duration and total subagent tokens) for all 21 runs. Durations include permission-classifier waits and runs executing in parallel, so they are not directly comparable to the previous baseline's figures (n=6). Against the 2026-07-31 baseline, mean pass rate is down 0.08, mean time up 102.3s, and mean tokens up 27396. `run_summary.delta` follows aggregate_benchmark.py, which subtracts a without-skill run this benchmark does not have, so it equals the with-skill means.
