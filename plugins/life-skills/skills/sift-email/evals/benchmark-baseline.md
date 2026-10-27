# Skill Benchmark: sift-email

**Executor**: claude-sonnet-5 (the CLI's default model on the recording machine, as the trial events name it)
**Grader**: claude-opus-5-5
**Date**: 2026-10-27
**Evals**: 1-40 (2 runs each, with_skill only)
**Driver**: `bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/sift-email/evals`, run twice in parallel with separate `TRIALS_DIR`s

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 718/734 (97.8%): 361/367 run 1, 357/367 run 2 |
| Evals passing both runs | 27/40 |
| Time | 193.6s ± 79.3s |
| Tokens | 1,328,292 ± 410,996 (total processed, dominated by cache reads) |
| Tool calls | 34.6 ± 13.4 |

Spreads are population standard deviations. Tokens are total processed per
trial (input + output + cache creation + cache read), rounded to whole tokens.

Every trial runs against the Gmail and Contacts stubs and a fake GitHub
(`evals/lib/github-fixture.py`). Graders checked labels, commits, and files
against each stub's final state and call log, not the trial's reply.

This baseline covers running sift on more than one Gmail account with one
rubric. Each account keeps its own `sift-email/state-<account>.md` with an
`Account:` line. Sift finds the account from the `authuser` in a
`get_thread` or `get_message` viewUrl, or else from the sender of the newest
sent mail. An older `state.md` is moved to the account's file with `git mv`
when one of its threads is in this account. A Labels row whose label this
account lacks stays, and sift creates the label when a thread fits the row.
Both runs were on the SKILL.md in this branch, on 2026-10-27, with fixtures
anchored to 2026-10-10 and shifted to the run date.

## What the evals found

27 of 40 evals passed in both runs, and every eval passed in at least one
run except 10 and 28.

Every trial that identified an account named it correctly and wrote only
that account's state file. With a second account sharing the rubric, sift
created `state-pat.work@example.com.md`, kept every rubric row, added an
inferred row for the account's own Clients label, created Travel for a
booking, and created no label for rows with no matching mail, leaving the
first account's state untouched (38). With no viewUrl, run 2 searched
`in:sent` for the account; run 1 found the right account from a thread's
`to` field instead (39). With an older `state.md`, both runs moved it to
`state-pat@example.com.md` in one commit (40).

The new rule that keeps rows for labels an account lacks also keeps the
Important, Needs reply, Sifted, and Wrong rows of an older rubric template,
which the previous rule removed because those labels were gone (28, both
runs). This was accepted: the only rubric in use is already current.

Failures:

| Cause | Misses | Evals |
|-------|--------|-------|
| A changelog line in the first person (1 run 1, 5 run 1, 18 run 2, 28 run 2, 40 run 2) | 5 | 1, 5, 18, 28, 40 |
| Kept the older template's Important, Needs reply, Sifted, and Wrong rows (both runs) | 2 | 28 |
| Added CATEGORY_PERSONAL to t-asked (6 run 2, 10 run 1) | 2 | 6, 10 |
| Took the account from a thread's `to` field without searching `in:sent` (run 1) | 1 | 39 |
| Searched contacts by the coach's domain, not address or name (run 2) | 1 | 2 |
| Read the gh stub's cassette instead of checking the repository's owner (run 2) | 1 | 10 |
| Left 21 changelog entries (run 2) | 1 | 15 |
| Labeled Gmail's important marketing Bulk, not Junk (run 2) | 1 | 16 |
| An order number in the commit message (run 2) | 1 | 23 |
| Quoted a rubric rule in the first person in the reply (run 1) | 1 | 32 |

Not graded, seen in a few trials: some trials read the harness's own files
in the run directory (`gh-cassette.json`, `gh-calls.log`, and
`github-seed.json`) or listed its bare repositories; a few commits had no
co-author line; and some runs added a second Statement row beside the
template's Receipt, Statement, Invoice row.

## Harness

- **Prompts.** Every eval prompt is `/sift-email`. Evals 10 and 14 add that
  the run was started by a schedule, with no one to answer; eval 13 adds the
  request to archive junk. Eval 1 has a follow-up turn naming the repository.
- **Stub.** The Gmail stub takes a top-level `"view_url_style": "authuser"`
  and then returns viewUrls in the live connector's format,
  `https://mail.google.com/mail/?authuser=<me>#all/<id>`. Every fixture sets
  it.
- **Fixtures.** Each fixture's `sift-email/state.md` is renamed
  `state-pat@example.com.md` and gains an `Account:` line; fixture 10's
  other user keeps its `state.md`. Eval 38 is new, a second account
  with its own Gmail and fixture 5's repository; eval 39 is fixture 37
  with no viewUrls and a sent thread; eval 40 is fixture 37 with the older
  `state.md`.
- **Isolation** is unchanged from the previous baseline.

## Per-eval results

| Eval | Scenario | Run 1 | Run 2 | Time r1 (s) | Time r2 (s) | Calls r1 | Calls r2 | Tokens r1 | Tokens r2 |
|------|----------|-------|-------|-------------|-------------|----------|----------|-----------|-----------|
| 1 | First run: ask, then create files and labels | 10/11 | 11/11 | 304.7 | 327.6 | 53 | 60 | 2,206,522 | 2,492,922 |
| 2 | Sender context; star by message | 13/13 | 12/13 | 248.8 | 248.3 | 50 | 44 | 1,368,875 | 1,299,598 |
| 3 | Real purchase from label history | 9/9 | 9/9 | 135.2 | 140.2 | 28 | 27 | 1,191,691 | 1,043,613 |
| 4 | Bulk, Junk, and Low priority | 9/9 | 9/9 | 141.8 | 171.3 | 28 | 39 | 951,130 | 1,245,122 |
| 5 | Daily review reaches the threshold | 10/11 | 11/11 | 298.7 | 198.4 | 38 | 35 | 1,769,201 | 1,389,464 |
| 6 | Daily review: nothing is a signal | 9/9 | 8/9 | 262.0 | 232.6 | 33 | 34 | 1,520,658 | 1,413,179 |
| 7 | User's edits stand on new replies | 10/10 | 10/10 | 283.4 | 267.6 | 40 | 36 | 1,596,310 | 1,491,920 |
| 8 | Gmail's Important mark vs the user's | 8/8 | 8/8 | 271.2 | 223.4 | 40 | 37 | 1,598,563 | 1,401,409 |
| 9 | New reply in a sifted thread | 8/8 | 8/8 | 132.8 | 162.8 | 27 | 26 | 1,150,195 | 1,111,948 |
| 10 | Another user's checkout is skipped | 8/9 | 8/9 | 110.8 | 102.0 | 22 | 15 | 812,626 | 653,019 |
| 11 | Nothing new: cheap exit | 5/5 | 5/5 | 36.5 | 42.4 | 12 | 13 | 326,945 | 558,117 |
| 12 | Archive granted for Junk | 7/7 | 7/7 | 164.9 | 127.5 | 39 | 33 | 1,574,454 | 1,256,970 |
| 13 | Archive asked, not granted | 8/8 | 8/8 | 140.9 | 134.4 | 24 | 23 | 1,131,143 | 1,027,766 |
| 14 | gh not logged in | 8/8 | 8/8 | 129.5 | 108.0 | 19 | 20 | 825,525 | 661,784 |
| 15 | Oversized rubric consolidation | 10/10 | 9/10 | 351.6 | 384.4 | 37 | 38 | 2,136,231 | 2,277,950 |
| 16 | Existing marks are context | 9/9 | 8/9 | 171.8 | 166.0 | 35 | 37 | 1,374,461 | 1,323,543 |
| 17 | About me as memory | 11/11 | 11/11 | 167.3 | 144.5 | 31 | 35 | 1,343,348 | 1,290,366 |
| 18 | Whole-inbox backlog, two pages | 11/11 | 10/11 | 245.0 | 291.5 | 88 | 86 | 1,951,301 | 1,326,379 |
| 19 | Label the rubric asks for | 9/9 | 9/9 | 189.8 | 186.8 | 41 | 36 | 1,430,755 | 1,168,258 |
| 20 | Tidy About me into groups | 9/9 | 9/9 | 124.8 | 180.7 | 29 | 33 | 1,328,207 | 1,402,806 |
| 21 | Category labels by what a message is | 13/13 | 13/13 | 286.4 | 309.5 | 65 | 68 | 1,571,812 | 1,305,836 |
| 22 | Newsletters lists decide Bulk | 10/10 | 10/10 | 168.4 | 177.2 | 26 | 30 | 1,037,507 | 1,296,808 |
| 23 | Mail meant for the user, not Bulk | 11/11 | 10/11 | 177.6 | 243.8 | 41 | 42 | 1,339,301 | 1,828,581 |
| 24 | Newsletter reaches the threshold | 10/10 | 10/10 | 182.7 | 242.6 | 34 | 26 | 1,433,094 | 1,235,746 |
| 25 | Learned newsletter conflicts with the user's line | 8/8 | 8/8 | 134.2 | 194.8 | 23 | 32 | 1,122,837 | 1,437,939 |
| 26 | Tabs by the rubric, over Gmail | 12/12 | 12/12 | 325.5 | 188.5 | 43 | 40 | 1,584,582 | 1,238,711 |
| 27 | User-set tab vs Gmail's re-sort | 8/8 | 8/8 | 212.3 | 232.3 | 29 | 33 | 1,129,862 | 1,249,888 |
| 28 | Older rubric brought up to date | 9/10 | 8/10 | 353.6 | 398.7 | 46 | 36 | 2,032,517 | 1,683,674 |
| 29 | Evidence rewrites the user's rule | 7/7 | 7/7 | 225.9 | 143.3 | 38 | 28 | 1,373,633 | 1,011,105 |
| 30 | New Gmail tab added to the table | 8/8 | 8/8 | 150.2 | 146.1 | 28 | 29 | 1,179,646 | 1,203,339 |
| 31 | Rubric overrides skill defaults | 5/5 | 5/5 | 137.4 | 124.3 | 24 | 26 | 996,117 | 948,946 |
| 32 | Close call becomes an (inferred) rule | 9/10 | 10/10 | 165.4 | 188.4 | 36 | 42 | 1,164,205 | 1,452,148 |
| 33 | Search finds only the user's private repo | 10/10 | 10/10 | 136.4 | 155.3 | 28 | 28 | 1,147,813 | 1,202,918 |
| 34 | No usable rubric: ask before writing | 7/7 | 7/7 | 44.6 | 81.8 | 9 | 17 | 323,887 | 673,409 |
| 35 | User label cataloged and applied | 11/11 | 11/11 | 389.4 | 173.5 | 48 | 31 | 2,434,347 | 1,347,035 |
| 36 | Existing label used, any case | 9/9 | 9/9 | 142.8 | 130.8 | 30 | 26 | 1,170,441 | 955,879 |
| 37 | Daily review due, no new mail: tidy and commit | 8/8 | 8/8 | 116.7 | 122.8 | 27 | 30 | 1,287,292 | 1,339,714 |
| 38 | Second account shares the rubric | 11/11 | 11/11 | 209.2 | 227.7 | 39 | 46 | 1,818,504 | 2,105,054 |
| 39 | Account from sent mail | 7/8 | 8/8 | 269.3 | 158.9 | 34 | 30 | 1,405,897 | 1,325,282 |
| 40 | Older state file moved to the account's | 7/7 | 6/7 | 127.1 | 143.9 | 27 | 29 | 1,074,756 | 1,369,032 |
