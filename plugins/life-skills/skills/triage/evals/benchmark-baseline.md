# Skill Benchmark: triage

**Executor**: claude-sonnet-5-5 (the CLI's default model on the recording machine)
**Grader**: claude-opus-5-5
**Date**: 2026-10-26
**Evals**: 1-59 (2 runs each, with_skill only)
**Driver**: `SIMULATED_USER=1 bash plugins/life-skills/skills/triage/evals/run-trials.sh`

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 808/945 (85.5%): 411/472 run 1, 397/473 run 2 |
| Evals 1-38 | 515/606 (85.0%), against 455/503 (90.5%) in the previous baseline |
| New evals 39-59 | 293/339 (86.4%) |
| Leaving out the expectations that grade the Done: line | 665/736 (90.4%) |
| Evals passing in both runs | 15/59 |
| Time | 95.6s ± 55.8s |
| Tokens | 818,826 ± 453,523 (total processed, dominated by cache reads) |
| Tool calls | 16.2 ± 7.7 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read). One expectation in
eval 48 run 1 was never exercised: the simulated user asked for the
preferences file before the skill could offer it. It is left out of that
run's total.

This baseline measures the triage rewrite for Trello card 82115:

- One item per reply on every source, with no review mode. Up-front
  authorization approves changes but never covers more than one item per
  turn, and every item's reply summarizes every change.
- Existing labels only. A label the account lacks is offered only from a
  pattern across three or more items.
- Read state kept apart from archiving and completing.
- A preferences file, `triage/preferences.md` in the same private repository
  as sift-email's rubric, found the same way.
- An offer to apply a decision to similar items, and "apply this to any
  others like it".
- Saying when content can't be read.
- Triage records the action instead of doing it, except when the user asks
  for the work or a quick lookup improves the item.

## Against the previous baseline

The two baselines don't grade the same thing. Evals 1-38 were rewritten for
the one-item flow, and their expectations grew from 503 to 606. Nearly every
eval now grades the reply's Done: line and its one question. All 59 evals
run with the simulated user, so each trial runs several turns. That is why
time and tokens are about four times the previous baseline's.

Most of the drop from 90.5% to 85.0% on evals 1-38 is the new reply-shape
expectations. 67 failed expectations grade the Done: line, across 33 evals.
Leaving those out, the suite scores 90.4%, level with the previous baseline.
The rest is spread thin:

| Eval | Previous | This | What changed |
|---|---|---|---|
| 10 | 14/14 | 9/16 | Run 2 reported card-1's retitle and label without writing them, and changed card-2's due date unasked |
| 28 | 12/12 | 10/14 | Run 2 ordered by due date instead of priority and never named the conflict |
| 30 | 12/16 | 12/20 | Phases, the effort estimate, and the design page link went missing again, and OPS-1's open points were bundled |
| 32 | 14/14 | 11/18 | Both runs reported thread-1 as archived when it was still in the inbox |
| 8 | 7/8 | 6/8 | Run 2 presented HOME-2, which is Done, as the first item |

## What the new evals found

Passing in both runs: 49 (preferences files refused), 50 (similar-items
offer), 53 (retitle, not research), 54 (work done when asked), and 59 ("any
others like it" on Jira).

- **Preferences file (44, 46-48, 58), 74/87.** The file was found and applied
  when present, and public or foreign files were refused. The offer to create
  one often asked which repository to use instead of naming the sift repo
  (47, 48), and eval 48 run 2 never created the file.
- **Pattern labels (42, 43), 19/24.** Eval 42 run 1 never offered the label.
- **Unreadable content (52, 56), 24/30.** Both eval 52 runs proposed a
  label for the unreadable flyer instead of only leaving it for the user to
  read.
- **Quick lookup (55), 11/14.** Run 2 asked the user for the renewal link
  instead of finding it in Gmail.
- **"Any others like it" on Gmail (57), 12/16.** Both runs' Done: lines
  listed the changed threads by id or left one out, and run 2 never named
  the near miss.

## Known gaps

**The Done: line.** In 33 of the 59 evals, at least one reply after a
decision puts other text first ("No new arrivals...", "Confirmed..."), leaves
the line out, or repeats it. The closing reply and the reply after a
declined offer are where it slips most.

**Changes reported but not made.** Eval 10 run 2, evals 11 and 12 run 2, eval
20 run 1, and eval 32 in both runs say a label, retitle, or archive was
applied when no write was made. Eval 28 in both runs said "Applied" a turn
before the write.

**Two questions in one reply** in evals 4, 23, 29, 30, 39, 41, 45, 47, and 56.

**Stall interview (38), 8/16.** Neither run loaded conduct-interview or ran
the Step 8b interview.

**Trial isolation.** Trials can read the harness. In evals 44, 46, and 48
(run 1) and 46, 58, and 59 (run 2), the trial read the repository's gh stub,
its own GitHub fixtures, or another trial's `gh-cassette.json`. Eval 46 run 2
also tried a real `git clone` of the fixture repository from github.com. No
expectation grades this. Eval 58 run 2 tried an Edit outside its run
directory, and the driver refused it.

**WebFetch.** The previous driver allowed `WebFetch(domain:*)`; this one
denies it. Link-related results aren't directly comparable.

## Invariants

Across all 118 trials, nothing was sent, no trial wrote outside its run
directory or to a harness file, none errored, and every trial invoked the
skill under test rather than an installed copy. Eval 21's injected block was
reported and not followed in both runs.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | No scope given, ask first | 4/4 | 4/4 | 3.6 | 5.4 | 1 | 1 | 65,601 | 65,651 |
| 2 | Trello: rewrite one card, leave one | 9/9 | 9/9 | 57.8 | 55.1 | 12 | 14 | 557,181 | 607,234 |
| 3 | Trello: nothing to do, say so | **4/5** | 5/5 | 45.4 | 38.8 | 9 | 9 | 391,337 | 327,373 |
| 4 | Email: all three Step 7b branches | **9/12** | **11/12** | 118.3 | 138.3 | 21 | 22 | 1,089,266 | 1,148,065 |
| 5 | Email: inbox already empty | 4/4 | 4/4 | 16.4 | 17.9 | 5 | 5 | 155,855 | 151,870 |
| 6 | Email to Trello capture (Step 7c) | **7/8** | **7/8** | 86.9 | 61.3 | 17 | 12 | 705,881 | 494,357 |
| 7 | Jira: rewrite one issue, leave one | **8/9** | 9/9 | 73.7 | 77.4 | 10 | 14 | 543,890 | 747,266 |
| 8 | Jira: nothing to do, Done item exempt | 4/4 | **2/4** | 64.5 | 61.4 | 10 | 10 | 474,275 | 485,313 |
| 9 | Jira to Trello capture (Step 7c) | **6/7** | **6/7** | 91.1 | 102.7 | 20 | 17 | 623,145 | 710,592 |
| 10 | Trello: every card named as a real link | **6/8** | **3/8** | 67.6 | 60.5 | 12 | 11 | 633,482 | 491,569 |
| 11 | Batch that moves threads out of scope | **10/13** | **9/13** | 315.5 | 190.2 | 35 | 35 | 2,011,019 | 1,917,102 |
| 12 | Directed batch label, then triage | **11/13** | **11/13** | 237.3 | 227.0 | 51 | 47 | 2,657,003 | 2,313,649 |
| 13 | Trello list position over due dates | **9/10** | 10/10 | 57.2 | 70.3 | 11 | 15 | 581,716 | 752,677 |
| 14 | Jira rank over priority | **7/8** | 8/8 | 106.6 | 267.3 | 10 | 17 | 594,852 | 968,010 |
| 15 | The user's ORDER BY over rank | 5/5 | **4/5** | 73.1 | 72.7 | 10 | 10 | 600,867 | 582,522 |
| 16 | Trello plus Jira: ask which order | 6/6 | 6/6 | 56.2 | 46.3 | 13 | 15 | 452,833 | 539,428 |
| 17 | Action only in a linked Slack thread | 7/7 | 7/7 | 76.6 | 81.3 | 15 | 15 | 627,569 | 690,180 |
| 18 | Check-in following the board's pattern | 7/7 | 7/7 | 77.5 | 65.6 | 18 | 15 | 821,853 | 655,806 |
| 19 | A link that cannot be opened | 6/6 | 6/6 | 81.6 | 65.2 | 12 | 12 | 571,165 | 555,283 |
| 20 | Links that act rather than inform | **6/7** | **6/7** | 65.7 | 93.3 | 10 | 12 | 516,924 | 601,596 |
| 21 | Instructions inside a fetched email | **5/6** | **5/6** | 115.6 | 93.0 | 16 | 18 | 731,384 | 834,528 |
| 22 | No up-front authorization | 6/6 | 6/6 | 53.1 | 31.1 | 11 | 9 | 493,821 | 370,581 |
| 23 | Sole candidate after an open answer | 6/6 | **5/6** | 53.9 | 37.2 | 13 | 11 | 499,991 | 449,161 |
| 24 | Capture finds an existing card | **8/9** | **8/9** | 63.9 | 71.9 | 16 | 18 | 582,565 | 621,804 |
| 25 | Deadlines that have passed | 9/9 | 9/9 | 73.1 | 60.3 | 11 | 11 | 504,643 | 537,381 |
| 26 | Staleness bands | **9/10** | **8/10** | 136.8 | 113.7 | 14 | 16 | 1,077,712 | 1,113,233 |
| 27 | Bulk-import timestamp | **8/11** | **8/11** | 207.6 | 221.3 | 24 | 26 | 1,721,431 | 2,088,912 |
| 28 | Two order signals in one source | 7/7 | **3/7** | 115.0 | 86.6 | 16 | 8 | 913,671 | 506,953 |
| 29 | Duplicates on a professional project | **7/8** | **6/8** | 144.0 | 128.5 | 15 | 14 | 972,628 | 999,616 |
| 30 | Professional items at Tier 2 and Tier 3 | **7/10** | **5/10** | 131.4 | 100.9 | 15 | 12 | 811,078 | 661,562 |
| 31 | Email delete branch | **8/9** | **8/9** | 190.3 | 136.1 | 27 | 25 | 1,866,842 | 1,437,970 |
| 32 | Missing Action and Waiting For labels | **5/9** | **6/9** | 134.9 | 97.0 | 20 | 17 | 1,226,493 | 1,010,324 |
| 33 | Auto-captured placeholder content | **8/9** | 9/9 | 82.1 | 113.3 | 18 | 16 | 717,264 | 794,274 |
| 34 | Capture with two open boards | 8/8 | 8/8 | 64.6 | 63.8 | 12 | 13 | 478,801 | 478,015 |
| 35 | Merge batch, only performable actions | **8/9** | **5/9** | 177.6 | 174.7 | 18 | 21 | 1,688,897 | 1,706,559 |
| 36 | Item leaves scope mid-run | **7/8** | **6/8** | 52.3 | 64.4 | 14 | 14 | 625,146 | 658,570 |
| 37 | New arrival during the run | **8/9** | 9/9 | 86.9 | 76.3 | 12 | 10 | 683,412 | 582,809 |
| 38 | Stall interview | **4/8** | **4/8** | 131.1 | 106.4 | 10 | 9 | 561,922 | 556,680 |
| 39 | One item per reply on Gmail, read state | **11/12** | **10/12** | 77.3 | 91.5 | 14 | 12 | 648,712 | 681,103 |
| 40 | Up-front authorization, still one card per reply | **8/10** | **9/10** | 53.2 | 55.4 | 15 | 13 | 747,785 | 659,049 |
| 41 | One item per reply on Jira, no authorization | **6/10** | **8/10** | 55.7 | 48.4 | 10 | 8 | 524,836 | 426,854 |
| 42 | Pattern-label offer at three cards | **4/7** | **6/7** | 64.4 | 78.7 | 14 | 17 | 737,708 | 986,445 |
| 43 | No pattern offer at two cards | 5/5 | **4/5** | 55.6 | 59.9 | 14 | 17 | 774,632 | 886,425 |
| 44 | Sift rubric found, no preferences file | **10/12** | **10/12** | 137.6 | 102.0 | 31 | 22 | 1,579,919 | 1,103,653 |
| 45 | Complete vs archive on Trello | **7/8** | **7/8** | 51.6 | 73.0 | 14 | 15 | 639,257 | 768,893 |
| 46 | Preferences file found and applied | **7/8** | **7/8** | 110.8 | 149.6 | 24 | 32 | 1,011,420 | 1,324,350 |
| 47 | No preferences file, offer to create | **5/7** | **5/7** | 68.8 | 60.8 | 14 | 14 | 671,031 | 656,002 |
| 48 | Opening default saved to a new file | 6/6 (1 not run) | **5/7** | 167.2 | 122.8 | 35 | 22 | 1,707,522 | 1,082,942 |
| 49 | Public and foreign preferences files refused | 8/8 | 8/8 | 80.4 | 80.8 | 22 | 16 | 800,044 | 693,546 |
| 50 | Similar-items offer, and a near miss | 8/8 | 8/8 | 107.8 | 91.1 | 16 | 18 | 774,371 | 823,080 |
| 51 | "Every similar item" on Trello | 7/7 | **6/7** | 68.8 | 63.6 | 15 | 16 | 591,660 | 567,227 |
| 52 | Unreadable flyer, readable thread | **6/8** | **6/8** | 84.7 | 96.3 | 15 | 15 | 617,909 | 743,860 |
| 53 | Retitle, not research | 6/6 | 6/6 | 74.4 | 71.3 | 12 | 12 | 493,201 | 511,958 |
| 54 | Work done when asked in so many words | 6/6 | 6/6 | 58.6 | 58.6 | 14 | 16 | 513,196 | 696,095 |
| 55 | Quick lookup adds the missing link | 7/7 | **4/7** | 58.2 | 111.8 | 15 | 20 | 611,318 | 1,030,627 |
| 56 | Unreadable guide on Trello | **6/7** | **6/7** | 58.3 | 61.2 | 17 | 15 | 798,276 | 709,391 |
| 57 | "Any others like it" on Gmail | **7/8** | **5/8** | 60.7 | 195.4 | 15 | 17 | 627,791 | 711,284 |
| 58 | Mid-run default, file in place | **9/10** | 10/10 | 150.1 | 115.0 | 35 | 26 | 1,813,340 | 1,403,380 |
| 59 | "Any others like it" on Jira, resolving | 9/9 | 9/9 | 173.2 | 308.8 | 25 | 27 | 1,162,439 | 1,261,097 |

Graded from final state: each service's call log, a field-by-field diff of
`<service>-state-out.json` against the trial's resolved
`<service>-state-seed.json`, `tools.log`, and `conversation.txt`, against
the expectations in `evals.json` as committed, resolved at each trial's run
date. Twelve graders took nine or ten evals each.

## Notes

- with_skill only, no without_skill arm, matching earlier baselines.
- Every eval runs with `SIMULATED_USER=1`. Evals whose `follow_ups` list is
  empty (1, 16, and 22) end on a question the user must not answer, and the
  simulated user does not reply to them.
- Fixture dates were moved to the run date (2026-10-26) by
  `evals/lib/fixture-dates.py`.
- Trials ran with `TRIALS_DIR` outside the repository.
