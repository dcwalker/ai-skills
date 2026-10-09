# Skill Benchmark: conduct-interview

**Model**: claude-sonnet-5
**Date**: 2026-07-31T15:45:00Z
**Evals**: 1, 2, 3, 4, 5, 6, 7, 8 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 100% ± 0% |
| Time | 136.5s ± 20.1s |
| Tokens | 87428 ± 20543 |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 4/4 | 104.6 | 33263 |
| 2 | 3/3 | 168.3 | 97507 |
| 3 | 3/3 | 121.4 | 96748 |
| 4 | 3/3 | 142.8 | 92715 |
| 5 | 3/3 | 161.6 | 95155 |
| 6 | 3/3 | 135.3 | 92374 |
| 7 | 3/3 | 138.7 | 95278 |
| 8 | 3/3 | 119.0 | 96385 |

## Notes

- In the ORIGINAL 2026-07-29 baseline run, 12 of 13 expectation-groups passed across 8 evals; eval 1's one genuine failure (two Step 2 interview turns bundling multiple distinct questions into one turn) was later fixed and re-run at 4/4 (see the final note), which is what the tables above reflect.
- This is a with_skill-only baseline (no without_skill comparison) since conduct-interview is a workflow skill, not a content-generation skill.
- All evals are pure conversational simulations (no git fixtures or gh-stub) -- the executor plays both the skill and the simulated user in a single agent turn, then a separate grader agent independently re-reads the resulting transcript.
- No systemic eval-design issues were flagged by any grader.
- 2026-07-31: after the original baseline's eval 1 finding, the one-question rule was redefined around the line of inquiry: a clarifying follow-up that narrows the same inquiry may share a turn, while asks about different subjects may not, regardless of punctuation. Eval 1's first expectation was updated to grade that distinction and the eval re-run against the amended skill: 4/4, with single-inquiry turns throughout, a separate-turn clarifying follow-up on a vague answer, and a [confirm ...] marker resolved only when the user supplied the fact. The per-eval row above reflects the re-run (run_number 2 in the JSON); the token drop for eval 1 also reflects the re-run using a different measurement context than the original batch.

## Per-turn baseline: evals 9-11 (2026-10-09)

Evals 9-11 run through `evals/lib/run-mcp-trials.sh` with `SIMULATED_USER=1`, so a separate model plays the user from each eval's private `simulated_user` briefing, and are graded turn by turn with this directory's `grade-turns.py`. Three runs per eval, against SKILL.md as of this commit. Rates count only turns the grader judged; a question-free turn, or a new topic after the user closed the last one, is not counted.

| Eval | One line of inquiry | Builds on answers |
|------|---------------------|-------------------|
| 9 (follow up an aside) | 10/11 (91%) | 6/7 (86%) |
| 10 (use a correction) | 10/12 (83%) | 5/6 (83%) |
| 11 (resist batching) | 27/29 (93%) | 14/15 (93%) |
| **All** | **47/52 (90%)** | **25/28 (89%)** |

The failures fall into four patterns:

- A housekeeping ask attached to a content question or to the Step 3 check ("confirm the month for the 17th", twice).
- Step 1 format and length asked together (twice; Step 1 lists them as one item, so the skill invites this).
- A wrap-up turn pairing feelings with "anything else you want" (once).
- Moving on from something just volunteered without following it up: a blocker raised in passing, an unreachable colleague (twice).

The transcript-level checks held in every run: the corrected "promotion" frame never came back in eval 10, and no eval 11 turn listed several report sections at once. The model grader varies by about one borderline turn per trial between gradings of the same transcript, so treat a difference of a turn or two as noise. Eval 10's first three runs are not counted: without "ask me questions first" in the prompt the skill never triggered.

## After tightening the one-question rule and follow-ups (2026-10-09)

Same three evals, three runs each, same grader, against the SKILL.md that splits Step 1's length and format, makes housekeeping and wrap-up asks their own inquiry, keeps the Step 3 question alone, and rereads each answer for anything new before changing the subject.

| Eval | One line of inquiry (before → after) | Builds on answers (before → after) |
|------|--------------------------------------|------------------------------------|
| 9 | 10/11 → 17/17 | 6/7 → 8/9 |
| 10 | 10/12 → 15/15 | 5/6 → 5/9 |
| 11 | 27/29 → 32/32 | 14/15 → 13/13 |
| **All** | **47/52 (90%) → 64/64 (100%)** | **25/28 (89%) → 26/31 (84%)** |

The one-question rule held in every turn of every run, against five bundled turns before. Builds-on-answers did not move beyond noise. Of the five turns marked down after the change, a reread finds one clear miss (eval 9: the user asked to discuss the secondary's coverage and the next question went to the disk alerts) and one arguable one; the other three follow from the answer or move on after a complete one, and the grader's own reason on one of them says nothing was left to explore. Conversations got longer, since asks that used to share a turn now take their own: trials cost $17.27 in all, against $12.45 before.
