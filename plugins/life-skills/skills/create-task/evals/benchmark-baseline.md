# Skill Benchmark: create-task

**Executor**: claude-opus-5-5
**Grader**: claude-opus-5-5
**Date**: 2026-11-19
**Evals**: 1-16 (2 runs with the skill, 1 run without it)
**Driver**: `TRIALS_DIR="$TMPDIR/create-task-trials" bash plugins/life-skills/skills/create-task/evals/run-trials.sh`

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Expectations passed | 150/150 (100%) | 56/75 (75%) | +25 points |
| Time | 21.7s ± 11.5s | 14.9s ± 6.3s | +6.7s |
| Tokens | 70,146 ± 39,117 | 58,088 ± 39,460 | +12,058 |

Tokens are total processed per trial (input, output, cache creation, and
cache read). Every eval is single-turn, so no simulated user runs. The
without-skill runs come from the fourth iteration; the fifth changed only
the skill and one expectation in eval 14, which was graded on those runs
too.

## Per-eval results

| Eval | Case | With skill, run 1 | With skill, run 2 | Without skill |
|------|------|-------------------|-------------------|---------------|
| 1 | hard-deadline-with-resources | 7/7 | 7/7 | 6/7 |
| 2 | soft-target-no-due-date | 3/3 | 3/3 | 3/3 |
| 3 | check-in-promised-date | 5/5 | 5/5 | 3/5 |
| 4 | combined-contexts | 5/5 | 5/5 | 4/5 |
| 5 | reference-not-task | 5/5 | 5/5 | 0/5 |
| 6 | project-needs-event-date | 4/4 | 4/4 | 2/4 |
| 7 | vague-title-asks | 3/3 | 3/3 | 2/3 |
| 8 | files-preauthorized-card | 6/6 | 6/6 | 3/6 |
| 9 | finds-duplicate-card | 3/3 | 3/3 | 3/3 |
| 10 | drafts-without-filing | 4/4 | 4/4 | 2/4 |
| 11 | splits-by-context | 5/5 | 5/5 | 5/5 |
| 12 | one-trip-one-task | 3/3 | 3/3 | 3/3 |
| 13 | email-to-self-format | 4/4 | 4/4 | 4/4 |
| 14 | prose-format | 6/6 | 6/6 | 6/6 |
| 15 | markdown-checklist-format | 4/4 | 4/4 | 4/4 |
| 16 | meeting-action-items | 8/8 | 8/8 | 6/8 |

## Notes

- The skill's largest effect is on what is not a plain task. Without it,
  the wifi password became a to-do with the password in it (eval 5), "plan
  the party" was restated as the task with no question about the date
  (eval 6), a "help me write a to-do" request was filed to Trello unasked
  (eval 10), and a preauthorized card was filed without its label or the
  search for a duplicate (eval 8).
- Evals 2, 9, and 11 to 15 pass without the skill too. They guard the
  content rules and the formats (prose, Markdown, an email to self) against
  regressions rather than measure the skill's lift.
- This is the fifth iteration. Earlier ones surfaced problems the skill now
  covers, each with an expectation: a date the user stated disputed against
  the machine's clock, a Links line naming a source with no link, a password
  repeated back, an unrequested step, a to-do offered for reference
  information (eval 5), an unchecked weekday (evals 1 and 14), dates from a
  meeting held "today" flagged as passed (eval 16), and a deadline the user
  never gave (eval 14).
- Outside the expectations, both eval 11 runs made the email to Priya wait
  for the landlord's yes, which the request never said, and one eval 1 run
  said the DMV office is closed on Saturday without checking.
