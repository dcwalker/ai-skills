# Skill Benchmark: transcribe-apple-notes-to-dayone

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine)
**Grader**: claude-opus-5-5
**Date**: 2026-10-14
**Evals**: 1-11 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/utilities/skills/transcribe-apple-notes-to-dayone/evals`, run twice with `TRIALS_DIR` under `$TMPDIR`

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 100/100 (100%): 50/50 run 1, 50/50 run 2 |
| Evals passing both runs | 11/11 |
| Time | 35.0s ± 20.2s |
| Tokens | 239,836 ± 150,874 (total processed, dominated by cache reads) |
| Tool calls | 10.6 ± 6.1 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read).

Every trial is one unattended `claude -p` turn against three fail-closed
stubs from `evals/lib`: `osascript-stub` for Apple Notes, `dayone-stub` for
the Day One CLI, and `swift-stub` for handwriting recognition, which returns
canned text with planted recognition errors. Graders checked entries, notes,
and calls against each stub's final state and call log, and the order of
commands in `events.jsonl`, not the trial's reply. All 22 trials loaded the
skill.

## What the evals found

The suite changed the skill twice before this baseline, and both changes are
in the PR:

- **Step 1 asked for settings the request already gave.** In the first full
  run, evals 2, 4, 5, 10, and 11 stopped to confirm the default batch size
  and corrections and the "exact" folder for "my iCloud Notes folder", and
  asked before running the checks that would answer them. Step 1 now checks
  sign-in, journals, and folders first (with a new `notes.py folders`),
  applies the two defaults without asking, and asks only for a missing
  source, journal, or done folder.
- **A request to fix an imported entry did not load the skill.** One eval 9
  trial edited the entry in place with `--entry-id` and reported success,
  though the stub, like the real CLI, kept the old text. The description now
  covers correcting an imported entry. Eval 11 trials also ignored the
  request to delete notes; Step 1 now requires the reply to answer it first.
- **The delete confirmation did not say why.** Eval 9 trials asked to delete
  the old entry without explaining that the CLI cannot edit an entry with an
  image, and one said the entry had no tags, which the CLI cannot know. The
  fixing section now lists what the confirmation must say. Eval 9 was rerun
  in both runs after this change; the other ten evals ran on text identical
  except for that section, which only eval 9 reaches.

Two observations that no expectation grades: eval 6 trials sometimes
extracted the images of notes outside the batch (but recognized and imported
only the batch), and one eval 2 trial flagged `2*3` as an uncertain reading
while keeping it as written.

## Harness

- Trials ran under `$TMPDIR`, outside the repo, so no ancestor `AGENTS.md`
  loaded, and with the private HOME and sandbox `run-mcp-trials.sh` provides.
- Trials with these fixtures run with `TZ=America/Chicago`; entry dates are
  graded as instants.
- Run 2, eval 4 logged one unconfirmed write to `/tmp/claude/tmpdir_path`. It
  was a read of a missing file; nothing landed outside the run directory.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | Clean batch of three, tag reminder | 9/9 | 9/9 | 61.3 | 74.0 | 18 | 24 | 448,428 | 382,464 |
| 2 | Lines that look like Markdown | 5/5 | 5/5 | 35.6 | 40.7 | 14 | 14 | 346,743 | 348,370 |
| 3 | Mixed note and a typed password note | 5/5 | 5/5 | 24.2 | 17.9 | 6 | 6 | 102,451 | 102,826 |
| 4 | Drawing stored twice | 5/5 | 5/5 | 61.9 | 65.5 | 17 | 17 | 421,922 | 426,069 |
| 5 | Narrow image held for PDF export | 4/4 | 4/4 | 42.1 | 46.2 | 16 | 14 | 383,686 | 317,846 |
| 6 | Batch size of two | 4/4 | 4/4 | 51.1 | 55.0 | 16 | 15 | 329,755 | 426,666 |
| 7 | No journal or folders named | 4/4 | 4/4 | 14.2 | 11.6 | 4 | 4 | 74,738 | 74,597 |
| 8 | dayone CLI signed out | 4/4 | 4/4 | 16.3 | 13.8 | 4 | 4 | 75,426 | 74,724 |
| 9 | Fix an imported entry with an image | 4/4 | 4/4 | 37.0 | 48.8 | 10 | 14 | 257,716 | 382,640 |
| 10 | Named journal does not exist | 3/3 | 3/3 | 14.9 | 11.4 | 4 | 4 | 75,007 | 74,776 |
| 11 | Asked to delete the notes | 3/3 | 3/3 | 11.5 | 15.4 | 4 | 4 | 74,895 | 74,648 |

Per-expectation evidence for every run is in `benchmark-baseline.json`.
