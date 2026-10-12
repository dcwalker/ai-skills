# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5-5 (the CLI's default model on the recording machine)
**Grader**: claude-opus-5-5
**Date**: 2026-10-12
**Evals**: 1-21 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 310/310 (100%): 155/155 run 1, 155/155 run 2 |
| Evals passing both runs | 21/21 |
| Time | 133.1s ± 50.0s |
| Tokens | 732,213 ± 226,633 (total processed, dominated by cache reads) |
| Tool calls | 34.2 ± 16.8 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial is one unattended `claude -p` turn against the Gmail, Claude Docs,
and Contacts stubs, and every eval checks that the run finishes without
waiting on the user. Graders checked labels, docs, and comments against each
stub's final state and call log, not the trial's reply.

The skill sets `disable-model-invocation`, so a plain request no longer
starts it. Every eval prompt begins with `/sift-email`, and every trial ran
the skill through that slash command.

Both runs were on 2026-10-12 in the fixtures' rubric timezone. The fixtures
are anchored to 2026-10-10 and were not shifted. Graders held "the run date"
to the date the run's clock gave in that timezone.

## What the evals found

Every eval passed in both runs.

Held in every trial: each run read the clock once in the rubric's timezone
and used that date for every log heading, changelog entry, and About me note;
the cheap empty-run path (11) wrote one "nothing new" line after searching
the rubric only for its Timezone line; the whole-inbox backlog (18) labeled
all 56 threads across two search pages; category labels (19, 21) were judged
on what a message is, under AI/; permission grants were carried out (12) and
ungranted actions were neither done nor offered (13); a missing Docs
connector did not stop labeling (14); unclear corrections kept their labels
and opened one `Sift:` question (6); answered questions were applied (10);
About me served as memory (17); consolidation kept every user rule and named
only the replaced senders (15); and tidying regrouped About me without
changing any words (20).

Not graded, seen in a few trials: first person for the user in doc text
(eval 5 run 1, tracked in #112), a log summary whose counts disagree with the
labels applied (eval 2 run 1), About me notes with a thin or wrong source,
lookups of a sender About me already covers, user labels searched by name
instead of id, Step 2 checks skipped, and replies opening with process
narration.

## Date check

Not part of the scores. Evals 5, 15, and 20, whose changelog dates failed in
the previous baseline, were run once more with the trial machine at UTC+14
(`TZ=Pacific/Kiritimati`), a day ahead of the rubric's timezone, the same
mismatch a cloud routine on UTC has in a western timezone's evening. Each
read the clock in the rubric's timezone and wrote only that date
(2026-10-12) in its log heading, changelog entries, and About me notes; none
wrote the machine's date (2026-10-13).

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
| 1 | First run: create docs and labels | 9/9 | 9/9 | 167.5 | 133.3 | 38 | 32 | 923,633 | 731,578 |
| 2 | Sender context; Needs reply by message | 11/11 | 11/11 | 202.7 | 225.1 | 50 | 53 | 1,171,478 | 1,186,558 |
| 3 | Real purchase from label history | 7/7 | 7/7 | 81.4 | 87.2 | 23 | 25 | 471,183 | 544,717 |
| 4 | Junk compared with Low priority | 7/7 | 7/7 | 107.2 | 122.6 | 37 | 33 | 678,304 | 645,198 |
| 5 | AI/Wrong with a clear direction | 9/9 | 9/9 | 143.0 | 160.4 | 35 | 34 | 703,186 | 721,059 |
| 6 | AI/Wrong unclear: question, no block | 8/8 | 8/8 | 126.3 | 126.6 | 32 | 29 | 800,357 | 731,808 |
| 7 | Swapped and added labels | 6/6 | 6/6 | 131.4 | 125.7 | 24 | 24 | 590,136 | 502,839 |
| 8 | Removed label | 5/5 | 5/5 | 145.0 | 119.4 | 21 | 23 | 444,287 | 601,546 |
| 9 | New reply in a sifted thread | 6/6 | 6/6 | 110.8 | 91.0 | 28 | 24 | 724,652 | 543,248 |
| 10 | Answered question applied | 7/7 | 7/7 | 112.4 | 110.4 | 20 | 26 | 688,414 | 781,472 |
| 11 | Nothing new: cheap exit | 6/6 | 6/6 | 42.2 | 42.1 | 17 | 18 | 340,661 | 334,796 |
| 12 | Archive granted for Junk | 4/4 | 4/4 | 90.1 | 120.7 | 29 | 34 | 588,024 | 864,667 |
| 13 | Archive asked, not granted | 6/6 | 6/6 | 72.1 | 112.9 | 32 | 31 | 658,719 | 627,990 |
| 14 | Docs connector missing | 7/7 | 7/7 | 69.7 | 52.8 | 21 | 15 | 568,878 | 424,045 |
| 15 | Oversized rubric consolidation | 9/9 | 9/9 | 183.7 | 186.8 | 23 | 23 | 638,444 | 715,096 |
| 16 | Existing labels are context | 7/7 | 7/7 | 125.9 | 172.5 | 39 | 50 | 794,938 | 1,337,115 |
| 17 | About me as memory | 9/9 | 9/9 | 105.6 | 136.6 | 33 | 33 | 757,838 | 791,809 |
| 18 | Whole-inbox backlog, two pages | 8/8 | 8/8 | 246.6 | 262.6 | 90 | 99 | 1,293,731 | 1,097,297 |
| 19 | Label the rubric asks for, under AI/ | 6/6 | 6/6 | 163.4 | 126.1 | 41 | 35 | 883,804 | 680,904 |
| 20 | Tidy About me into groups | 8/8 | 8/8 | 131.7 | 116.6 | 28 | 25 | 783,676 | 680,238 |
| 21 | Category labels by what a message is | 10/10 | 10/10 | 199.4 | 198.8 | 55 | 56 | 781,935 | 922,686 |
