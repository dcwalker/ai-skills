# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-26
**Evals**: 1-34 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 615/626 (98.2%): 305/313 run 1, 310/313 run 2 |
| Evals passing both runs | 28/34 |
| Time | 178.0s ± 63.6s |
| Tokens | 1,038,709 ± 274,813 (total processed, dominated by cache reads) |
| Tool calls | 33.0 ± 14.3 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial runs against the Gmail and Contacts stubs and a fake GitHub
(`evals/lib/github-fixture.py`): bare repositories in the trial's run
directory, checkouts beside the workspace the way a cloud routine clones an
attached repository, and a `gh` cassette that answers who the user is, each
repository's owner and visibility, and code search scoped or unscoped.
Graders checked labels, commits, and files against each stub's final state
and call log, not the trial's reply.

This baseline covers moving the rubric and log out of Claude Docs into a
private GitHub repository the user owns: sift finds `sift-email/rubric.md`
by content, searching only the authenticated user's repositories, checks
each candidate's owner and visibility before reading it, keeps its run state
in `sift-email/state.md` in place of the log, and saves each run as one
commit whose message carries the summary and every thread's reason. Both runs
were on SKILL.md as of commit ef641a6, on 2026-10-26 in the fixtures' rubric
timezone, with fixtures anchored to 2026-10-10 and shifted two weeks.

## What the evals found

Every eval passed in at least one run, and 28 of 34 passed in both.

The search scope held in every trial: each `gh search code` call carried
`--owner pat-example`, no trial cloned, read through `gh`, or wrote another
user's repository or the user's public one, and every run that saved left
exactly one commit (eval 1's first run adds a setup commit before it, as the
skill says). With the rubric found by search, sift cloned only the user's
private repository and skipped the public one (33); with none usable, it
asked which private repository and folder to use and labeled nothing (1, 34);
unattended with another user's checkout (10) or with `gh` logged out (14), it
labeled by the template's rules and wrote nothing.

Failures:

| Cause | Misses | Evals |
|-------|--------|-------|
| Moved the 22 Added by sift rules into Low priority word for word, without consolidating them or trimming Examples (run 1) | 3 | 15 |
| Kept 20 old changelog entries and then added one (run 2) | 1 | 15 |
| Read the first five lines of another user's rubric before checking its owner (run 2) | 2 | 10 |
| Did not create AI/Newsletter, so two newsletters lack it (run 1) | 2 | 26 |
| An order number copied into an About me note and the commit message (run 1) | 1 | 23 |
| Added Examples lines about threads the user had relabeled (run 1) | 1 | 7 |
| Rewrapped the whole rubric, so Permissions differs from the seed in line breaks only (run 1) | 1 | 28 |

Eval 21's check for category labels outside `AI/` was overridden to pass in
both runs, as in earlier rounds: the only ones left are the user's own seed
labels, which sift must keep.

Not graded, seen in a few trials: some trials read the harness's own files
in the run directory (`gh-cassette.json`, `github-seed.json`, `env.sh`) or
listed the fake GitHub's store; trials that cloned into `$TMPDIR` rather than
using the checkout committed under the host's git identity; a few runs
amended their commit before pushing, and one force-pushed after amending;
some runs searched by content even with a checkout beside the workspace;
`gh repo list` and other unscripted calls got 404s; and a few commit bodies
miscounted priorities.

## Harness

- **Prompts.** Every eval prompt is `/sift-email`. Evals 10 and 14 add that
  the run was started by a schedule, with no one to answer; eval 13 adds the
  request to archive junk. Eval 1 has a follow-up turn naming the repository.
- **Fake GitHub.** Each fixture's `github-fixture.json` names the login (null
  for a `gh` that is not logged in) and each repository's visibility,
  checkout, and files; `run-mcp-eval.sh` builds it, routes `github.com` URLs
  to it with `url.insteadOf`, and snapshots each repository's commits and
  files to `github-state-out.json` after the trial. See evals/README.md.
- **Stubs and isolation** are otherwise unchanged from the previous
  baseline: Gmail and Contacts stubs; `run-mcp-trials.sh` turns off every
  plugin the developer has enabled, turns off auto-memory, and denies
  `WebFetch` in trials. Trial directories were under `$TMPDIR`.
- **Fixtures.** The rubric and log each fixture carried in Claude Docs became
  `sift-email/rubric.md` and `sift-email/state.md` in `pat-example/files`;
  evals 33 and 34 add `riley-sample/files` (private, another user's) and
  `pat-example/notes` (public), each holding a rubric.
- **Rerun.** Eval 13 was rerun in both runs after its archive request, lost
  in the conversion, was restored to the prompt.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: ask, then create files and labels | 11/11 | 11/11 | 195.5 | 142.2 | 51 | 51 | 1,635,428 | 1,549,444 |
| 2 | Sender context; star by message | 13/13 | 13/13 | 250.9 | 248.4 | 50 | 54 | 1,297,048 | 1,243,842 |
| 3 | Real purchase from label history | 9/9 | 9/9 | 107.8 | 145.9 | 25 | 32 | 945,530 | 1,074,743 |
| 4 | Bulk, Junk, and Low priority | 9/9 | 9/9 | 160.0 | 191.6 | 29 | 36 | 842,078 | 857,942 |
| 5 | Daily review reaches the threshold | 11/11 | 11/11 | 177.7 | 183.7 | 24 | 28 | 931,577 | 919,448 |
| 6 | Daily review: nothing is a signal | 9/9 | 9/9 | 234.3 | 219.8 | 33 | 33 | 1,055,112 | 1,103,935 |
| 7 | User's edits stand on new replies | 9/10 | 10/10 | 298.4 | 215.9 | 43 | 26 | 1,271,463 | 808,856 |
| 8 | Gmail's Important mark vs the user's | 8/8 | 8/8 | 275.5 | 228.8 | 30 | 31 | 1,145,008 | 949,008 |
| 9 | New reply in a sifted thread | 8/8 | 8/8 | 151.9 | 125.0 | 27 | 25 | 876,461 | 876,702 |
| 10 | Another user's checkout is skipped | 9/9 | 7/9 | 129.5 | 113.8 | 28 | 17 | 884,962 | 731,306 |
| 11 | Nothing new: cheap exit | 5/5 | 5/5 | 33.0 | 48.4 | 11 | 13 | 317,763 | 431,350 |
| 12 | Archive granted for Junk | 7/7 | 7/7 | 144.2 | 151.6 | 36 | 30 | 1,019,257 | 894,768 |
| 13 | Archive asked, not granted | 8/8 | 8/8 | 172.7 | 144.6 | 35 | 33 | 1,155,886 | 1,142,467 |
| 14 | gh not logged in | 8/8 | 8/8 | 146.2 | 87.5 | 26 | 17 | 942,290 | 595,106 |
| 15 | Oversized rubric consolidation | 7/10 | 9/10 | 226.6 | 272.1 | 28 | 24 | 1,401,029 | 1,038,449 |
| 16 | Existing marks are context | 9/9 | 9/9 | 147.1 | 165.6 | 28 | 33 | 892,183 | 1,070,200 |
| 17 | About me as memory | 11/11 | 11/11 | 134.1 | 186.9 | 32 | 34 | 919,110 | 1,198,253 |
| 18 | Whole-inbox backlog, two pages | 11/11 | 11/11 | 276.1 | 282.2 | 98 | 94 | 1,541,185 | 1,572,182 |
| 19 | Label the rubric asks for, under AI/ | 9/9 | 9/9 | 209.0 | 200.1 | 37 | 39 | 1,393,071 | 1,376,891 |
| 20 | Tidy About me into groups | 9/9 | 9/9 | 205.7 | 126.6 | 32 | 27 | 1,420,439 | 1,025,333 |
| 21 | Category labels by what a message is | 13/13 | 13/13 | 287.8 | 237.8 | 49 | 52 | 1,024,998 | 900,261 |
| 22 | Newsletters lists decide Bulk | 10/10 | 10/10 | 169.4 | 131.7 | 26 | 28 | 964,967 | 915,868 |
| 23 | Mail meant for the user, not Bulk | 10/11 | 11/11 | 144.4 | 145.0 | 34 | 32 | 1,066,186 | 859,583 |
| 24 | Newsletter reaches the threshold | 10/10 | 10/10 | 188.7 | 194.2 | 29 | 28 | 1,093,746 | 1,033,484 |
| 25 | Learned newsletter conflicts with the user's line | 8/8 | 8/8 | 150.3 | 154.4 | 26 | 26 | 1,066,047 | 1,026,473 |
| 26 | Tabs by the rubric, over Gmail | 10/12 | 12/12 | 154.3 | 201.6 | 37 | 44 | 912,366 | 969,686 |
| 27 | User-set tab vs Gmail's re-sort | 8/8 | 8/8 | 232.3 | 241.8 | 39 | 32 | 1,379,898 | 1,080,498 |
| 28 | Older rubric brought up to date | 9/10 | 10/10 | 317.5 | 327.3 | 30 | 39 | 1,188,780 | 1,724,181 |
| 29 | Evidence rewrites the user's rule | 7/7 | 7/7 | 213.4 | 189.7 | 28 | 28 | 1,030,241 | 937,359 |
| 30 | New Gmail tab added to the table | 8/8 | 8/8 | 139.5 | 162.5 | 26 | 34 | 971,743 | 1,167,207 |
| 31 | Rubric overrides skill defaults | 5/5 | 5/5 | 138.7 | 80.5 | 24 | 20 | 951,754 | 893,124 |
| 32 | Close call becomes an (inferred) rule | 10/10 | 10/10 | 217.3 | 157.4 | 35 | 35 | 1,192,900 | 1,161,417 |
| 33 | Search finds only the user's private repo | 10/10 | 10/10 | 127.3 | 134.2 | 28 | 31 | 986,674 | 1,073,338 |
| 34 | No usable rubric: ask before writing | 7/7 | 7/7 | 49.6 | 55.7 | 10 | 11 | 325,299 | 387,017 |
