# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5-5 (the CLI's default model on the recording machine)
**Grader**: claude-opus-5-5
**Date**: 2026-10-11
**Evals**: 1-18 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals $(seq 1 18)`, run twice

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 255/260 (98%): 127/130 run 1, 128/130 run 2 |
| Evals passing both runs | 16/18 |
| Time | 93.7s ± 33.2s |
| Tokens | 610,912 ± 173,641 (total processed, dominated by cache reads) |
| Tool calls | 26.3 ± 14.5 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

This is the skill's first baseline (issue #109). Every trial is one unattended
`claude -p` turn against the Gmail, Claude Docs, and Contacts stubs, and every
eval checks that the run finishes without waiting on the user. Graders checked
labels, docs, and comments against each stub's final state and call log, not
the trial's reply. The run date was 2026-10-11, one day past the fixtures'
2026-10-10 anchor, so dates were not shifted.

## What the evals found

Passing in both runs: 2-14 and 16-18.

- **First-run links (1), 8/9 in both runs.** Both runs gave the new docs' links
  in chat and asked for them in the routine prompt, but left them out of the
  log summary, which Step 6 also asks for. The links matter most in chat, where
  the user reads them on the first run; the log copy is the gap.
- **Consolidation (15), 7/9 and 8/9.** Both runs consolidated the 22
  near-duplicate rules into 12, each naming one business and its own helper
  senders, with no open-ended category, and left every user rule untouched.
  Both missed the expectation of fewer than 10 rule lines. That expectation is
  stricter than the skill's rule that a consolidated rule names only the
  senders it replaces: twelve unrelated businesses do not merge without putting
  several on one line, which the skill never asks for. Run 1 also trimmed the
  changelog to 20 without adding an entry for the consolidation.

Held in every trial: the whole-inbox backlog (eval 18) labeled all 56 threads,
following the search onto its second page; Permissions grants were carried
out (eval 12 archived only the Junk thread, kept it unread, and reported it);
unclear corrections kept their labels and `AI/Wrong` and opened one `Sift:`
question (eval 6); answered questions were applied and acknowledged in their
thread (eval 10); About me served as memory (eval 17 used a cached note, added
a new one under its topic, and removed an expired one); Needs reply followed
the message, not the sender (evals 2, 6, 16, 17); existing labels, stars, and
Gmail's marker stayed context (eval 16); and no reply ended on an offer or
question in a graded case, no run fetched a doc link on the web, and no run
wrote to memory.

Not graded, seen in a few trials: rules that went a step past one correction
(eval 8 run 2), log text calling the user "the user" or "me" rather than Pat
or "you", a reply that put a paraphrase of the user's answer in quotation
marks (eval 10), an ungraded closing offer (eval 14 run 1), and searches by
label name rather than label id, which the stub and live Gmail both accept.

## Harness

- **Stubs.** New Claude Docs and Contacts stubs; the Gmail stub gained
  `label_thread`, `unlabel_thread`, paging, relative-date and name-based label
  search, and the live response shapes for `list_labels` and `create_label`.
- **Atomic batch.** The Docs stub's `batch` did not yet roll back a refused
  batch when these trials ran; it was made atomic in the same change. One
  trial hit it (eval 2 run 2): a refused batch kept its earlier members, and
  the retry left the same final state.
- **Isolation.** `run-mcp-trials.sh` now turns off every plugin the developer
  has enabled, turns off auto-memory, and denies `WebFetch` in trials. These
  apply to every suite on the shared driver; see evals/README.md.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: create docs and labels | 8/9 | 8/9 | 91.8 | 115.2 | 28 | 38 | 606,465 | 807,824 |
| 2 | Sender context; Needs reply by message | 11/11 | 11/11 | 155.1 | 128.8 | 38 | 36 | 775,427 | 899,911 |
| 3 | Labels on earlier threads; real purchase | 7/7 | 7/7 | 76.4 | 59.2 | 17 | 18 | 510,959 | 456,013 |
| 4 | Junk compared with Low priority | 7/7 | 7/7 | 66.9 | 65.4 | 21 | 22 | 470,093 | 467,831 |
| 5 | AI/Wrong with a clear direction | 9/9 | 9/9 | 120.6 | 122.3 | 33 | 30 | 591,134 | 822,061 |
| 6 | AI/Wrong unclear: question, no block | 8/8 | 8/8 | 91.3 | 114.5 | 25 | 26 | 775,999 | 678,503 |
| 7 | Swapped and added labels | 6/6 | 6/6 | 102.6 | 105.9 | 21 | 19 | 537,386 | 605,162 |
| 8 | Removed label | 5/5 | 5/5 | 110.5 | 88.0 | 21 | 18 | 326,264 | 530,445 |
| 9 | New reply in a sifted thread | 6/6 | 6/6 | 81.5 | 80.8 | 24 | 21 | 687,552 | 600,947 |
| 10 | Answered question applied | 7/7 | 7/7 | 108.1 | 52.4 | 20 | 19 | 534,842 | 583,714 |
| 11 | Nothing new | 5/5 | 5/5 | 44.8 | 59.8 | 14 | 17 | 370,949 | 498,058 |
| 12 | Archive granted for Junk | 4/4 | 4/4 | 66.7 | 74.4 | 21 | 19 | 572,493 | 521,864 |
| 13 | Archive asked, not granted | 6/6 | 6/6 | 72.9 | 124.5 | 27 | 33 | 561,509 | 969,302 |
| 14 | Docs connector missing | 7/7 | 7/7 | 44.2 | 44.9 | 15 | 16 | 403,270 | 399,927 |
| 15 | Oversized rubric consolidation | 7/9 | 8/9 | 149.7 | 121.6 | 18 | 18 | 677,313 | 537,970 |
| 16 | Existing labels are context | 7/7 | 7/7 | 79.0 | 67.8 | 26 | 23 | 503,505 | 540,159 |
| 17 | About me as memory | 9/9 | 9/9 | 75.2 | 84.9 | 22 | 23 | 578,006 | 659,517 |
| 18 | Whole-inbox backlog, two pages | 8/8 | 8/8 | 141.6 | 183.0 | 79 | 82 | 741,045 | 1,189,408 |
