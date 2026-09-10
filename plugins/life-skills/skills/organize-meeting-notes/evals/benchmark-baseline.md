# Skill Benchmark: organize-meeting-notes

**Model**: claude-sonnet-5 (executor) / claude-opus-5 (analyzer)
**Date**: 2026-09-10T23:52:14Z
**Evals**: 1-20 (1 recorded run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Pass Rate | 98% ± 5% |
| Time | 186.9s ± 79.7s (n=20) |
| Tokens | 90208 ± 10893 (n=20) |

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
| 9 | 5/6 | 363.8 | 109476 |
| 10 | 5/5 | 147.8 | 85957 |
| 11 | 6/6 | 219.4 | 88823 |
| 12 | 5/5 | 152.3 | 87444 |
| 13 | 6/6 | 196.1 | 87637 |
| 14 | 6/6 | 190.5 | 92199 |
| 15 | 9/11 | 286.0 | 104184 |
| 16 | 4/4 | 36.7 | 70750 |
| 17 | 7/7 | 190.9 | 95927 |
| 18 | 7/7 | 323.5 | 112320 |
| 19 | 7/7 | 244.0 | 100920 |
| 20 | 4/4 | 77.7 | 76082 |

## Notes

- 20 evals pass 109/112 expectations, 18 of them fully. Results were verified against ground truth rather than executor self-report: every card URL in a final document was checked against `trello-calls.log`, and graders were told to flag any logged call the transcript does not show.
- This baseline accompanies drafting notes from meeting artifacts. When no raw notes exist, `references/draft-notes-from-artifacts.md` has the skill list the screenshots, audio transcripts, or chat transcripts it found, confirm before drafting, draft one note per decision or debate with attribution in the sentence, and review the draft section by section. Alongside it: a What Notes Should Capture section (action items, decisions and their reasons, disagreements, unresolved topics), a Step 3b Agenda section for any run with an agenda, action items that lead with an owner and keep due dates as said (adding the calendar date for an ambiguous weekday), no retry when a Trello card fails, and a summary rule that forbids invented causes and logistics.
- Evals 15-20 are new: 15 (a chat log only, with an agenda, a debate, a deferral, and an ownerless action), 16 (no notes and no artifacts), 17 (an audio transcript with a generic `Speaker 3` plus timestamped screenshots), 18 (screenshots only, including an undated photo), 19 (a "parking lot" deferral and an agenda item the meeting never reached), and 20 (the user declines drafting). Fixture screenshots for 17 and 18 carry legible content, since the images are the only record.
- Existing evals changed: 7 now expects the Agenda section and keeps its link in the note, 6 checks a "by Friday" due date, and 1 and 5 accept an initial expanded to the first name the user gives when asked, which Step 3 requires.
- Runs were recorded after two rounds of review. The first full run scored 100/112 and exposed real regressions (the Agenda section pulled a link out of its note, drafts retold chats message by message, the skill proposed names when asking who spoke or who owns an action) alongside eval wording that contradicted the skill. Evals 1, 4, 11, and 17 are recorded at run 2; 7, 9, 15, 18, and 19 at run 3; 20 at run 4. Eval 5's run 1 was regraded against its updated wording.
- Three runs were discarded for validity rather than results. Eval 20 run 1: the simulated user pasted notes, contradicting its own opening message. Eval 20 run 3: the prompt pre-declined the drafting offer, so the expectation was widened to accept acknowledging that answer. Eval 7 run 2: the executor made two Trello calls it did not record; run 3 was executed under an instruction to record every call.
- Two failures remain. Eval 9's summary overstated the notes in all three runs (a causal claim twice, then presenting untested work as underway), even after the summary rule gained its no-invented-causes clause, so the summary rule needs more than another clause. Eval 15 run 3 assigned the runbook update to its speaker and treated a shutdown timing as a due date without asking; runs 1 and 2 asked correctly, so this is intermittent.
- Trials ran as subagents with working directories outside the repository and the skill staged with `references/`. One run (eval 1 run 2) used the user's first name from the executor's own session context; it affected no expectation. Evals without a `trello-fixture.json` produce no call log, so their zero-call checks rest on the transcript plus the script's refusal to run without a fixture.
- Time and token figures rose against the previous baseline (60343 ± 6294 tokens, 151.6 ± 47.9s over 14 evals), driven by the longer skill, the artifact evals, and executors that now write a full transcript file, so they are not directly comparable.
- Not covered by any expectation: in eval 18 run 3 the skill still asked about Trello after the opening message said "No Trello for this one."
