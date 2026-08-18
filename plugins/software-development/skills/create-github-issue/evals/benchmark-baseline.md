# Skill Benchmark: create-github-issue

**Model**: claude-opus-5
**Date**: 2026-08-18T23:40:00Z
**Evals**: 1-11 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 41/43 (95%) |
| Evals fully passing | 10/11 |
| Time | 112.6s ± 28.0s |
| Tokens | 43,542 ± 1,976 |
| Tool calls | 11.6 ± 3.0 |

Measured against the skill as it now stands, after the two defects below were
fixed and the fixtures de-leaked. Both misses are in eval 9, one behaviour seen
twice. Spreads are population standard deviations.

## Per-eval results

| Eval | Scenario | Passed | Time (s) | Tokens | Tool calls |
|------|----------|--------|----------|--------|------------|
| 1 | Full flow, approve and create | 5/5 | 146.0 | 46,286 | 14 |
| 2 | Vague request — ask, don't draft | 4/4 | 65.3 | 40,499 | 7 |
| 3 | User declines — hold | 3/3 | 130.6 | 44,010 | 14 |
| 4 | One revision round, then create | 4/4 | 119.7 | 44,946 | 12 |
| 5 | Cross-reference a related issue | 3/3 | 134.7 | 44,471 | 14 |
| 6 | No repository given — ask | 4/4 | 55.0 | 39,828 | 6 |
| 7 | Requested label doesn't exist | 4/4 | 117.8 | 43,935 | 13 |
| 8 | Two revision rounds, then create | 3/3 | 141.6 | 46,333 | 15 |
| 9 | Group optional fields, suggest values | **2/4** | 99.2 | 42,710 | 10 |
| 10 | Creation fails — report, don't fake | 5/5 | 111.8 | 42,863 | 9 |
| 11 | Report the created issue as a link | 4/4 | 116.8 | 43,078 | 14 |

Graded from `gh-calls.log` and each trial's transcript. Create-call counts
verified per trial: exactly zero for evals 2, 3 and 6, exactly one for the other
eight — including eval 10, whose single call is the one that failed.

`check-trial-hygiene.sh` does not apply here and correctly refuses rather than
reporting a false pass: these fixtures are cassette-only with empty, non-git
workspaces, so it exits 2 with "checked nothing, so this is not a pass."

## Two skill defects, found by the first run and fixed before this one

An earlier run of this suite surfaced two defects that the suite itself could not
catch. Both are fixed; this baseline measures the fixed skill.

**`gh milestone list` was not a real `gh` subcommand.** Step 3 prescribed it,
five trials flagged it independently, and the cassettes answered it anyway — so
every trial's Step 3 "passed" here while failing against real `gh`. Step 3 now
uses `gh api "repos/OWNER/REPO/milestones" --jq '.[].title'`, and the nine
cassettes are re-keyed to match. Confirmed in this run: all eleven trials used
the API form, the old command appears in no log, and it now falls through to the
coverage-gap default so the fixtures can no longer hide a regression. Fixture 11,
which has no milestones, returns cleanly empty.

**Step 5 hardcoded `/tmp/github-issue-body.md`.** Step 7 then passed that same
fixed path to `--body-file`, so two concurrent sessions would read and write each
other's issue bodies — silently, with whichever body was written last being the
one filed. Step 5 now uses `mktemp` and echoes the path, warning that
`$BODY_FILE` will not survive between commands when each runs in a fresh shell.

The fix is what makes this run's method possible: **all eleven trials ran
concurrently**, where the previous run had to be serialised. Every trial got its
own path — `hO6Oqx`, `fBYAoh`, `afARzX`, `Hilem6`, `33CZ8T`, `nJ5Vx7`, `j7g4tz`,
`ysb5Tq`, `it1kTq` and the rest — and no two collided. Several trials confirmed
the fresh-shell warning earned its place, having had to carry the literal path
forward because the variable was gone by the next command.

## Three fixtures were telling trials the answer

Fixtures 2, 3 and 6 carried the graded behaviour in their cassette's `default`
stderr, which the stub prints on **any** unmatched `gh` call:

| Fixture | Leaked text |
|---------|-------------|
| 2 | `...the request was too vague to have reached discovery/creation yet` |
| 3 | `...issue creation should not be attempted after a decline` |
| 6 | `...no repository was ever established for this session, so repo-scoped discovery/creation calls are unexpected` |

Those are exactly the three restraint evals — the ones whose whole question is
whether the skill holds back unprompted. Executors are barred from reading
`evals.json`; the stub then handed them the conclusion anyway, and it fired
early: on a `gh repo list` probe, and on a Step 1 `gh api contents` probe made
before any draft existed.

Reduced to the generic message the other eight fixtures use. All three evals
scored the same before and after the fix (4/4, 3/3, 4/4), so the hint was not
load-bearing — each reaches its answer through the skill's required-field and
approval rules. It was still there to be used.

## Eval 9: suggesting nothing leaves nothing to approve

Eval 9 asks the skill to group its optional-field questions into one message and
to suggest values discovered from the repo, so the scripted "Yes, that's all
correct" can accept them. The grouping works. The suggesting does not.

The draft reads `Milestone: None`, with `v1.2 Release` appearing only as
"available", reasoned as "no existing issue is assigned to a milestone". The
create call is `--label enhancement` with no `--milestone`. Expectation 2 (the
draft shows the milestone) and expectation 3 (the create includes it) both fail;
expectations 1 and 4 pass.

**This is stable, not variance:** the same behaviour appeared in the first
benchmark run, in the post-fix verification trial, and again here — three
independent trials, identical outcome, including once with the milestone command
changed underneath it. So the failure has nothing to do with fetching milestones.

The judgment is defensible — the user never asked for a milestone. But Step 4
says to use discovered values to "form a suggested value" for every field and
present it for confirmation, which is what the eval encodes; declining to
suggest turns a blanket approval into a no-op. Graded as written. If the intended
behaviour is "suggest nothing the user didn't ask for", Step 4 and this eval both
need rewording.

## Skill gaps still open

- **Nothing covers the draft file on the decline or failure paths.** Step 8 says
  to clean up "after successful creation". Eval 3 declined and eval 10's create
  failed; both preserved the file by their own reasoning, and this run ends with
  exactly those two drafts left on disk. Almost certainly right, still unstated.
- **Step 1 assumes a local checkout.** Every fixture workspace is empty and not a
  git repo, so Step 1's document review finds nothing and Step 4's "infer from
  git remote" is dead. Trials reach for `gh api repos/OWNER/REPO/contents/...`
  instead and hit a cassette gap. The skill says what to read, not where to read
  it from when there is no clone.
- **No quality bar for the issue body.** The skill is thorough about *fields* and
  silent about *content*: nothing says to gather reproduction steps, expected vs
  actual, or environment when the description is thin. Eval 2's trial noted that
  with no `ISSUE_TEMPLATE` or `CONTRIBUTING.md` present, Step 5 gives no floor.

## Fixture gaps

- **Issue #42 doesn't exist in fixture 5.** The eval asks the skill to connect
  the new issue to "#42 about session timeouts". `gh issue view 42` misses the
  cassette and `gh issue list` returns titles without numbers, so the obvious
  thematic match cannot be confirmed as #42. The trial hedged with "likely
  related" rather than asserting it — correct, but the eval grades a
  cross-reference the fixture never exposes.
- **`gh api repos/.../contents/...` is uncovered in every fixture**, so the only
  route to repo-side templates and glossary returns a coverage-gap default.
- **Fixture 10's auth response is inconsistent with its create response.**
  `gh auth status` reports a healthy login while `issue create` returns 403
  "Resource not accessible by integration". Possible with a fine-grained token,
  but nothing hints at reduced scopes, so the diagnosis has to be inferred.
- **Stub output shape differs from real `gh`.** `gh label list` and
  `gh project list` return raw JSON without `--json`; real `gh` prints tables.

## What holds up

The draft-and-approve contract is solid, which is the core of this skill. No
trial created an issue before its approval, across one-round (evals 1, 5, 7, 9,
10, 11), two-round (eval 4) and three-round (eval 8) sessions. The three
restraint evals produced zero creates between them.

Honesty under failure is clean. Eval 10's create returned 403 and the trial said
so plainly, named three candidate causes, invented no issue number, and preserved
the draft for retry. Eval 7 discovered that a user-requested label did not exist,
said so in the draft, created with the valid label only, and repeated the
deviation in its closing message rather than letting the user assume both landed.

## Notes

- with_skill only, no without_skill arm: `create-github-issue` is a workflow
  skill.
- Scripted user replies are embedded in each eval's prompt, which lets a
  single-shot executor play out a multi-turn approval session honestly — a better
  design than the interactive-ordering expectations that had to be reworded in
  the `pr` suite.
- Evals 5 and 8 grade body *content*, but `--body-file` means `gh-calls.log`
  records only a path and Step 8 deletes the file. Those two executors were asked
  to quote the body verbatim before cleanup so the content was gradeable from an
  artifact rather than from a summary.
