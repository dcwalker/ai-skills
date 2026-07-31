# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5
**Date**: 2026-07-31T05:00:00Z
**Evals**: 1-6 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 108.0s ± 24.9s (n=6) |
| Tokens | 49307 ± 4853 (n=6) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 109.1 | 52287 |
| 2 | 4/4 | 62.5 | 43116 |
| 3 | 4/4 | 92.5 | 43339 |
| 4 | 4/4 | 139.4 | 55745 |
| 5 | 4/4 | 120.8 | 48102 |
| 6 | 4/4 | 123.7 | 53251 |

## Notes

- 6/6 evals pass 100% of their expectations in this baseline run. All results were independently verified against ground truth (the real `trello-calls.log` artifact each trial produced, or its absence for negative cases) rather than accepted from executor self-report alone — every self-reported call, URL, and error message matched the log exactly.
- This is the first skill baselined that needed the new `create-trello-task.sh` script (`plugins/life-skills/skills/organize-meeting-notes/scripts/`) and `TRELLO_FIXTURE_FILE`/`TRELLO_FIXTURE_COUNTS_DIR`/`TRELLO_FIXTURE_LOG` harness wiring in `evals/lib/run-eval.sh`, both new in this baseline. The script did not exist anywhere in the repo before this baseline despite the skill's SKILL.md referencing it as if it were already implemented — a real product gap (the same class of issue as `resolve-sonarqube-issues`' earlier hardcoded self-referential script path) found and fixed as part of establishing this baseline.
- This skill is almost entirely a multi-turn conversation skill (structurally close to `conduct-interview`) with no git state at all — evals have no `repo/` fixture, only an empty scratch workspace plus an optional `trello-fixture.json`. Since a real interactive back-and-forth can't happen against a canned eval prompt, each executor trial played both the assistant and a simulated user role internally, producing a full labeled transcript, and was graded on the shape and correctness of that simulated conversation plus the real, verifiable `trello-calls.log` artifact — not on any live human interaction.
- Evals 2, 3, and 5 deliberately ship with no `trello-fixture.json` at all (rather than an empty/no-op fixture), since the correct behavior in each is to never call `create-trello-task.sh`. Evidence for those trials' zero-call expectations is the absence of any `trello-calls.log` file, since the script only creates that file when actually invoked.
- Eval 6 surfaced one real, minor, unflagged-by-any-expectation deviation worth noting for future `review-code` skill-quality diffing: the executor inferred the simulated user's own name ("Dan Walker") from ambient session context (git config / user email) rather than asking, even though the skill's Step 1 says to ask for clarification on missing details rather than guess. This didn't fail any expectation in this eval (none of eval 6's expectations test "me"-attendee resolution specifically — that's what eval 1 tests, where the skill did ask), but it's a real edge case in how the skill handles an unnamed "me" attendee that a future eval could test more directly.
- This batch covered a strong mix of scenarios: a full happy path with an ambiguous initial and a duplicate attendee email resolved via asking, plus two successful Trello card creations (1); a genuinely empty-action-item case requiring explicit confirmation rather than silent omission (2); a user declining Trello creation after action items are already confirmed (3); a partial-failure case where one of two Trello calls fails and must not be silently masked or fabricated (4); the skill's documented time-mismatch correction rule combined with a non-attendance strikethrough (5); and an already-resolved ambiguous-initial case where the skill must use information already given rather than re-asking or guessing (6).
- The `tool_calls` and `errors` fields on every run are `null`, not measured — they aren't wired up in the executor/grader pipeline yet.
