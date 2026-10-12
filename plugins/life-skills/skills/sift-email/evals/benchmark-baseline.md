# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5-5 (the CLI's default model on the recording machine)
**Grader**: claude-opus-5-5
**Date**: 2026-10-11
**Evals**: 1-21 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals $(seq 1 21)`, run twice

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 306/310 (99%): 155/155 run 1, 151/155 run 2 |
| Evals passing both runs | 19/21 |
| Time | 113.2s ± 43.5s |
| Tokens | 723,296 ± 235,652 (total processed, dominated by cache reads) |
| Tool calls | 32.4 ± 16.1 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial is one unattended `claude -p` turn against the Gmail, Claude Docs,
and Contacts stubs, and every eval checks that the run finishes without
waiting on the user. Graders checked labels, docs, and comments against each
stub's final state and call log, not the trial's reply. The run date was
2026-10-11, one day past the fixtures' 2026-10-10 anchor, so dates were not
shifted.

Eval 11 was re-run once the Docs stub's guide documented the search read it
had been missing (the real connector's guide documents it). Its two re-runs
replace the round's first eval 11 results; every other eval is from the same
round.

## What the evals found

Passing in both runs: 1-10 and 12-19, 21.

- **Nothing new (11), 6/6 and 5/6.** Both runs took Step 2's cheap path:
  seven empty checks, no labels or rubric changed, one "nothing new" log
  line. Run 1 searched the rubric for its Timezone line; run 2 read the whole
  rubric for it, which the cheap path is meant to avoid. A quiet run costs
  about $0.21 either way, most of it the fixed cost of starting a run.
- **Tidy the rubric (20), 8/8 and 5/8.** Run 1 merged the duplicate soccer
  headings, moved the coach, practice, and auction notes where they belong,
  changed no words, and logged the reorganization. Run 2 skipped Step 3,
  said the rubric looked clean, and left all three problems, although the
  step says a fresh-looking rubric is no reason to skip it.

Held in every trial: the whole-inbox backlog (18) labeled all 56 threads
across two search pages; category labels (19, 21) were judged on what a
message is, under AI/, with no label for a question about a receipt, a fare
sale, or a lookalike security alert; permission grants were carried out (12)
and ungranted actions were neither done nor offered (13); a missing Docs
connector did not stop labeling (14); unclear corrections kept their labels
and opened one `Sift:` question (6); answered questions were applied (10);
About me served as memory (17); consolidation kept every user rule and named
only the replaced senders (15); and Needs reply followed the message, not the
sender (2, 6, 16, 17).

Not graded, seen in a few trials: log times copied from an earlier entry
instead of read from the clock, a summary whose counts disagree with the
labels applied (eval 18 run 2), the user called "the user" in log or rubric
text, rules a step wider than one correction, an About me note added from a
message alone or missed after a lookup, and replies closing with a suggestion
to add a Permissions grant.

## Harness

- **Stubs.** New Claude Docs and Contacts stubs; the Gmail stub gained
  `label_thread`, `unlabel_thread`, paging, relative-date and name-based label
  search, and the live response shapes for `list_labels` and `create_label`.
  The Docs stub's `batch` is atomic, and its guide documents search reads.
- **Isolation.** `run-mcp-trials.sh` turns off every plugin the developer has
  enabled, turns off auto-memory, and denies `WebFetch` in trials. These
  apply to every suite on the shared driver; see evals/README.md. One trial
  (eval 18) tried a Bash write outside its run directory in an earlier round,
  and the sandbox refused it.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: create docs and labels | 9/9 | 9/9 | 149.5 | 110.9 | 37 | 31 | 1,003,704 | 713,022 |
| 2 | Sender context; Needs reply by message | 11/11 | 11/11 | 130.9 | 167.7 | 41 | 50 | 761,648 | 1,110,921 |
| 3 | Real purchase from label history | 7/7 | 7/7 | 60.0 | 64.4 | 23 | 23 | 424,557 | 547,472 |
| 4 | Junk compared with Low priority | 7/7 | 7/7 | 103.9 | 87.4 | 34 | 30 | 694,065 | 659,836 |
| 5 | AI/Wrong with a clear direction | 9/9 | 9/9 | 104.9 | 193.4 | 29 | 38 | 609,972 | 1,107,160 |
| 6 | AI/Wrong unclear: question, no block | 8/8 | 8/8 | 132.8 | 120.7 | 31 | 29 | 798,820 | 802,826 |
| 7 | Swapped and added labels | 6/6 | 6/6 | 115.6 | 103.8 | 27 | 24 | 746,993 | 596,018 |
| 8 | Removed label | 5/5 | 5/5 | 122.1 | 130.5 | 24 | 23 | 712,072 | 683,990 |
| 9 | New reply in a sifted thread | 6/6 | 6/6 | 82.3 | 96.4 | 26 | 27 | 598,334 | 718,308 |
| 10 | Answered question applied | 7/7 | 7/7 | 101.2 | 110.3 | 25 | 28 | 606,933 | 707,096 |
| 11 | Nothing new: cheap exit | 6/6 | 5/6 | 43.6 | 43.4 | 19 | 19 | 343,646 | 386,029 |
| 12 | Archive granted for Junk | 4/4 | 4/4 | 69.6 | 77.4 | 29 | 29 | 633,426 | 716,704 |
| 13 | Archive asked, not granted | 6/6 | 6/6 | 81.9 | 84.0 | 28 | 23 | 603,497 | 578,579 |
| 14 | Docs connector missing | 7/7 | 7/7 | 56.0 | 44.1 | 15 | 11 | 476,024 | 333,955 |
| 15 | Oversized rubric consolidation | 9/9 | 9/9 | 179.1 | 136.1 | 21 | 23 | 577,739 | 714,982 |
| 16 | Existing labels are context | 7/7 | 7/7 | 87.5 | 174.3 | 32 | 42 | 693,733 | 1,410,082 |
| 17 | About me as memory | 9/9 | 9/9 | 123.5 | 149.0 | 33 | 36 | 903,477 | 991,779 |
| 18 | Whole-inbox backlog, two pages | 8/8 | 8/8 | 226.1 | 183.1 | 93 | 94 | 1,298,293 | 1,151,963 |
| 19 | Label the rubric asks for, under AI/ | 6/6 | 6/6 | 98.2 | 93.3 | 34 | 30 | 619,011 | 660,431 |
| 20 | Tidy About me into groups | 8/8 | 5/8 | 114.0 | 65.1 | 25 | 24 | 491,113 | 567,221 |
| 21 | Category labels by what a message is | 10/10 | 10/10 | 167.8 | 169.6 | 53 | 49 | 914,746 | 708,243 |
