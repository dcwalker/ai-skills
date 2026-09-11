# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5 (analyzer)
**Date**: 2026-09-11T01:20:28Z
**Evals**: 1-20 (1 recorded run each, 3 for eval 9, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 98% ± 7% |
| Time | 200.5s ± 90.7s (n=22) |
| Tokens | 91963 ± 12054 (n=22) |

## Per-eval results

| Eval | Pass Rate | Time (s) | Tokens |
|------|-----------|----------|--------|
| 1 | 5/5 | 199.0 | 88555 |
| 2 | 4/4 | 118.4 | 80313 |
| 3 | 4/4 | 121.3 | 84723 |
| 4 | 4/4 | 144.3 | 82397 |
| 5 | 4/4 | 142.1 | 80239 |
| 6 | 5/5 | 153.7 | 88636 |
| 7 | 7/7 | 257.4 | 101400 |
| 8 | 5/5 | 173.8 | 86170 |
| 9 (run 7) | 7/7 | 383.7 | 109305 |
| 9 (run 8) | 5/7 | 353.9 | 111493 |
| 9 (run 9) | 7/7 | 331.2 | 110451 |
| 10 | 5/5 | 147.8 | 85957 |
| 11 | 6/6 | 219.4 | 88823 |
| 12 | 5/5 | 152.3 | 87444 |
| 13 | 6/6 | 170.2 | 91114 |
| 14 | 7/7 | 182.9 | 85989 |
| 15 | 9/11 | 286.0 | 104184 |
| 16 | 4/4 | 36.7 | 70750 |
| 17 | 7/7 | 190.9 | 95927 |
| 18 | 7/7 | 323.5 | 112320 |
| 19 | 7/7 | 244.0 | 100920 |
| 20 | 4/4 | 77.7 | 76082 |

## Notes

- 20 evals and 22 recorded runs pass 124/128 expectations, with 18 evals passing every expectation in every recorded run. Results were verified against ground truth rather than executor self-report: every card URL in a final document was checked against `trello-calls.log`, and graders were told to flag any logged call the transcript does not show.
- This baseline accompanies drafting notes from meeting artifacts. When no raw notes exist, `references/draft-notes-from-artifacts.md` has the skill list the screenshots, audio transcripts, or chat transcripts it found by file name, confirm before drafting, draft one note per decision or debate with attribution in the sentence, and review the draft section by section. Alongside it: a What Notes Should Capture section (action items, decisions and their reasons, disagreements, unresolved topics), a Step 3b Agenda section for any run with an agenda, action items that lead with an owner and keep due dates as said (adding the calendar date for an ambiguous weekday), no retry when a Trello card fails, and a summary written as prose with one sentence per note.
- Evals 15-20 are new: 15 (a chat log only, with an agenda, a debate, a deferral, and an ownerless action), 16 (no notes and no artifacts), 17 (an audio transcript with a generic `Speaker 3` plus timestamped screenshots), 18 (screenshots only, including an undated photo), 19 (a "parking lot" deferral and an agenda item the meeting never reached), and 20 (the user declines drafting). Fixture screenshots for 17 and 18 carry legible content, since the images are the only record.
- Existing evals changed: 7 now expects the Agenda section and keeps its link in the note, 6 checks a "by Friday" due date, 1 and 5 accept an initial expanded to the first name the user gives when asked, which Step 3 requires, and 9 and 14 check that the summary reads as prose with no semicolons and no clauses chained with "and".
- The summary rule took three designs to pass eval 9. A list of prohibitions failed its accuracy check in three runs, twice by inventing a cause linking two facts. A pick, restate, join, and check procedure failed in three more, promoting proposals and approvals into completed decisions ("Priya proposed dropping staging" became "the team chose to drop" it), and one of those runs skipped its verification step. The PR review flagged the regression. The recorded rule gives each chosen outcome its own sentence drawn from a single note, keeping that note's subject and verb so its status survives, and eval 9's accuracy check passed in all three recorded runs.
- Eval 9 records all three runs of the current rule rather than the best one. Run 8 still built one sentence by chaining two clauses with "and", and split vendor support into its own section although the user tied it to the migration. Run 7 passed, though its grader noted a "since" in one sentence that implies a cause its note does not state.
- Recorded runs follow several review rounds. The first full run scored 100/112 and exposed real regressions (the Agenda section pulled a link out of its note, drafts retold chats message by message, the skill proposed names when asking who spoke or who owns an action) alongside eval wording that contradicted the skill. Evals 1, 4, 11, and 17 are recorded at run 2; 7, 13, 14, 15, 18, and 19 at run 3; 20 at run 4; 9 at runs 7 through 9. Eval 5's run 1 was regraded against its updated wording.
- Three runs were discarded for validity rather than results. Eval 20 run 1: the simulated user pasted notes, contradicting its own opening message. Eval 20 run 3: the prompt pre-declined the drafting offer, so the expectation was widened to accept acknowledging that answer. Eval 7 run 2: the executor made two Trello calls it did not record; run 3 was executed under an instruction to record every call.
- Eval 15 run 3 assigned the runbook update to its speaker and treated a shutdown timing as a due date without asking; runs 1 and 2 asked correctly, so this is intermittent.
- Trials ran as subagents with working directories outside the repository and the skill staged with `references/`. One run (eval 1 run 2) used the user's first name from the executor's own session context; it affected no expectation. Evals without a `trello-fixture.json` produce no call log, so their zero-call checks rest on the transcript plus the script's refusal to run without a fixture.
- Time and token figures rose against the previous baseline (60343 ± 6294 tokens, 151.6 ± 47.9s over 14 evals), driven by the longer skill, the artifact evals, and executors that now write a full transcript file, so they are not directly comparable.
- Not covered by any expectation: in eval 18 run 3 the skill still asked about Trello after the opening message said "No Trello for this one."
