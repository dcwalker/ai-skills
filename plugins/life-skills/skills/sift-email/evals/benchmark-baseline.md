# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5-5 (the CLI's default model on the recording machine)
**Grader**: claude-opus-5-5
**Date**: 2026-10-12
**Evals**: 1-21 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 307/310 (99%): 155/155 run 1, 152/155 run 2 |
| Evals passing both runs | 18/21 |
| Time | 132.1s ± 49.8s |
| Tokens | 728,490 ± 191,098 (total processed, dominated by cache reads) |
| Tool calls | 35.0 ± 18.2 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial is one unattended `claude -p` turn against the Gmail, Claude Docs,
and Contacts stubs, and every eval checks that the run finishes without
waiting on the user. Graders checked labels, docs, and comments against each
stub's final state and call log, not the trial's reply.

The skill sets `disable-model-invocation`, so a plain request no longer
starts it. Every eval prompt begins with `/sift-email`, and every trial ran
the skill through that slash command.

Both runs crossed midnight in the fixtures' rubric timezone, so trials read
2026-10-11 or 2026-10-12 from the clock. The fixtures are anchored to
2026-10-10 and were not shifted. Graders held "the run date" to the date the
clock gave in the rubric's timezone.

## What the evals found

Passing in both runs: 1-4, 6-14, 16-19, and 21.

- **Changelog dates (5, 15, 20), 9/9 and 8/9, 9/9 and 8/9, 8/8 and 7/8.**
  All three run 2 failures are the same bug: a changelog entry dated with the
  machine's local date while the run's log heading used the rubric
  timezone's date, a day later. Eval 5's run also never read the clock and
  wrote an invented log time.

Held in every trial: the cheap empty-run path (11) wrote one "nothing new"
line after searching the rubric only for its Timezone line; the whole-inbox
backlog (18) labeled all 56 threads across two search pages; category labels
(19, 21) were judged on what a message is, under AI/; permission grants were
carried out (12) and ungranted actions were neither done nor offered (13); a
missing Docs connector did not stop labeling (14); unclear corrections kept
their labels and opened one `Sift:` question (6); answered questions were
applied (10); About me served as memory (17); consolidation kept every user
rule and named only the replaced senders (15); tidying regrouped About me
without changing any words (20); and no trial wrote first person for the user
in doc text.

Not graded, seen in a few trials: an About me note dated with the machine's
local date beside a log heading in the rubric's date, About me notes added
when the lookups found nothing or given the wrong source, log entries missing
per-thread lines or count lines, user labels searched by name instead of id,
Step 2 checks skipped, and replies opening with process narration.

## Harness

- **Prompts.** Every eval prompt starts with `/sift-email`, followed by the
  rubric and log links (eval 1 gives none, for the first run).
- **Stubs and isolation** are unchanged from the previous baseline: Gmail,
  Claude Docs, and Contacts stubs; `run-mcp-trials.sh` turns off every plugin
  the developer has enabled, turns off auto-memory, and denies `WebFetch` in
  trials. See evals/README.md.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: create docs and labels | 9/9 | 9/9 | 139.9 | 154.4 | 36 | 37 | 733,652 | 909,796 |
| 2 | Sender context; Needs reply by message | 11/11 | 11/11 | 198.8 | 182.6 | 43 | 49 | 832,778 | 975,780 |
| 3 | Real purchase from label history | 7/7 | 7/7 | 89.1 | 88.5 | 26 | 27 | 553,846 | 618,134 |
| 4 | Junk compared with Low priority | 7/7 | 7/7 | 101.0 | 103.0 | 33 | 37 | 669,130 | 761,619 |
| 5 | AI/Wrong with a clear direction | 9/9 | 8/9 | 157.0 | 124.7 | 31 | 29 | 604,184 | 642,073 |
| 6 | AI/Wrong unclear: question, no block | 8/8 | 8/8 | 134.2 | 165.4 | 32 | 29 | 736,962 | 934,729 |
| 7 | Swapped and added labels | 6/6 | 6/6 | 145.2 | 137.4 | 24 | 26 | 707,399 | 670,278 |
| 8 | Removed label | 5/5 | 5/5 | 117.6 | 141.0 | 21 | 26 | 503,664 | 768,773 |
| 9 | New reply in a sifted thread | 6/6 | 6/6 | 102.8 | 125.6 | 25 | 30 | 569,237 | 856,640 |
| 10 | Answered question applied | 7/7 | 7/7 | 100.7 | 110.8 | 25 | 25 | 481,346 | 590,756 |
| 11 | Nothing new: cheap exit | 6/6 | 6/6 | 52.7 | 44.5 | 18 | 20 | 375,275 | 452,818 |
| 12 | Archive granted for Junk | 4/4 | 4/4 | 110.7 | 99.6 | 32 | 35 | 666,555 | 783,100 |
| 13 | Archive asked, not granted | 6/6 | 6/6 | 101.3 | 130.3 | 30 | 32 | 596,241 | 716,155 |
| 14 | Docs connector missing | 7/7 | 7/7 | 56.7 | 49.5 | 17 | 17 | 472,169 | 456,819 |
| 15 | Oversized rubric consolidation | 9/9 | 8/9 | 118.8 | 148.1 | 22 | 22 | 570,312 | 618,359 |
| 16 | Existing labels are context | 7/7 | 7/7 | 126.4 | 117.2 | 35 | 34 | 722,711 | 671,628 |
| 17 | About me as memory | 9/9 | 9/9 | 130.8 | 139.2 | 34 | 33 | 879,876 | 880,369 |
| 18 | Whole-inbox backlog, two pages | 8/8 | 8/8 | 259.7 | 245.1 | 95 | 97 | 1,095,660 | 1,081,827 |
| 19 | Label the rubric asks for, under AI/ | 6/6 | 6/6 | 128.3 | 105.2 | 39 | 37 | 826,726 | 610,578 |
| 20 | Tidy About me into groups | 8/8 | 7/8 | 144.6 | 128.0 | 25 | 32 | 725,505 | 1,029,674 |
| 21 | Category labels by what a message is | 10/10 | 10/10 | 260.7 | 232.3 | 72 | 81 | 1,165,650 | 1,077,800 |
