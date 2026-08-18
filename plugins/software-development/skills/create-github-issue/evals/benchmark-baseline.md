# Skill Benchmark: create-github-issue

**Model**: claude-opus-5
**Date**: 2026-08-18T23:10:00Z
**Evals**: 1-11 (1 run each, with_skill only)

## Summary

| Metric | With Skill |
|--------|------------|
| Expectations passed | 41/43 (95%) |
| Evals fully passing | 10/11 |
| Time | 115.2s ± 27.3s |
| Tokens | 43,095 ± 1,728 |
| Tool calls | 11.1 ± 2.7 |

Both misses are in eval 9, one behaviour seen twice. Spreads are population
standard deviations, matching the other baselines.

## Per-eval results

| Eval | Scenario | Passed | Time (s) | Tokens | Tool calls |
|------|----------|--------|----------|--------|------------|
| 1 | Full flow, approve and create | 5/5 | 128.5 | 44,504 | 13 |
| 2 | Vague request — ask, don't draft | 4/4 | 66.6 | 40,484 | 6 |
| 3 | User declines — hold | 3/3 | 81.0 | 40,773 | 9 |
| 4 | One revision round, then create | 4/4 | 146.1 | 44,638 | 15 |
| 5 | Cross-reference a related issue | 3/3 | 149.2 | 44,520 | 14 |
| 6 | No repository given — ask | 4/4 | 77.2 | 40,380 | 7 |
| 7 | Requested label doesn't exist | 4/4 | 138.4 | 43,993 | 11 |
| 8 | Two revision rounds, then create | 3/3 | 130.3 | 45,553 | 11 |
| 9 | Group optional fields, suggest values | **2/4** | 111.8 | 43,138 | 13 |
| 10 | Creation fails — report, don't fake | 5/5 | 127.7 | 43,066 | 11 |
| 11 | Report the created issue as a link | 4/4 | 110.5 | 42,998 | 12 |

Graded from `gh-calls.log` and each trial's transcript. Create-call counts were
verified per trial: exactly zero for evals 2, 3 and 6, exactly one for the other
eight — including eval 10, whose single call is the one that failed.

`check-trial-hygiene.sh` does not apply here and correctly refused rather than
reporting a false pass: these fixtures are cassette-only with empty, non-git
workspaces, so it exits 2 with "checked nothing, so this is not a pass."

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
`evals.json`; the stub then handed them the conclusion anyway. It fires early and
easily: eval 2 tripped it on a `gh repo list` probe, eval 3 on a Step 1
`gh api contents` probe made before it had drafted anything.

Eval 3's trial is the one that caught it, and diagnosed it correctly: that text
belongs on the `issue create` entry, where only an actual creation attempt would
surface it, not on the cassette-wide default every unmatched call reaches.

Fixed in this branch, reduced to the generic message the other eight fixtures
already use. **Evals 2 and 3 were then re-run against clean fixtures and scored
identically** (4/4 and 3/3) — both reach their answer through the skill's
required-field and approval rules, not through the hint. The recorded runs are
the clean ones; the leaked runs are kept alongside as `eval-N-LEAKED`.

## Eval 9: suggesting nothing leaves nothing to approve

Eval 9 asks the skill to group its optional-field questions into one message and
to suggest values discovered from the repo, so the scripted "Yes, that's all
correct" can accept them. The grouping worked. The suggesting did not.

The trial's draft reads `Milestone: None`, with `v1.2 Release` appearing only in
the discovery preamble as an available option marked "suggested: None". The
create call is `--label enhancement` with no `--milestone`. So expectation 2 (the
draft shows the milestone) and expectation 3 (the create includes it) both fail;
expectations 1 and 4 pass.

The underlying judgment is defensible — the user never asked for a milestone, and
attaching one unbidden is a real choice. But the skill's own Step 4 says to use
discovered values to "form a suggested value" for every field and present it for
confirmation, which is what the eval encodes. Declining to suggest turns the
blanket approval into a no-op. Graded as written; if the intended behaviour is
"suggest nothing the user didn't ask for", Step 4 and this eval both need
rewording.

## Skill defects the fixtures mask

**`gh milestone list` is not a real command.** Step 3 prescribes
`gh milestone list --repo OWNER/REPO`. Upstream `gh` has no `milestone`
subcommand — milestones come from `gh api repos/{owner}/{repo}/milestones`. Five
separate trials pointed this out. The cassette answers it happily, so this suite
can never catch it, and every trial's Step 3 would fail against a real `gh`.

**Step 5 hardcodes a shared absolute path.** `cat > /tmp/github-issue-body.md`,
then `--body-file "/tmp/github-issue-body.md"` in Step 7. Two concurrent
sessions on one machine read and write each other's issue bodies. This is why
these trials were run one at a time rather than in parallel like the previous six
suites, and it is a live hazard outside benchmarking too. `mktemp` fixes it.

**Nothing covers the decline or failure paths for the draft file.** Step 8 says
to clean up "after successful creation". Eval 3 declined and eval 10's create
failed; both preserved the file, which seems right, and both had to reason it out
themselves. Eval 10's leftover then had to be cleared before eval 11 could run.

**Step 1 assumes a local checkout.** Every fixture workspace here is empty and
not a git repo, so Step 1's document review finds nothing and Step 4's "infer
from git remote" is dead. Trials reasonably reached for
`gh api repos/OWNER/REPO/contents/...` instead and hit a cassette gap. The skill
says what to read but not where to read it from when there is no clone.

**No quality bar for the issue body.** The skill is thorough about *fields* and
silent about *content*: nothing says to gather reproduction steps, expected vs
actual, or environment when the description is thin. Eval 2's trial noted that
with no `ISSUE_TEMPLATE` or `CONTRIBUTING.md` present, Step 5 gives no floor, so
the skill could be read as licensing a one-line body from "there's a bug with
login sometimes". It asked anyway — on the required-repo rule, not on any
content rule.

## Fixture gaps

- **Issue #42 doesn't exist in fixture 5.** The eval asks the skill to connect
  the new issue to "#42 about session timeouts". `gh issue view 42` misses the
  cassette, and `gh issue list` returns titles without numbers, so the obvious
  thematic match cannot be confirmed as #42. The trial hedged with "possibly
  related" rather than asserting it — correct, but the eval grades a
  cross-reference the fixture never actually exposes.
- **`gh api repos/.../contents/...` is uncovered in every fixture**, so the only
  route to repo-side templates and glossary returns a coverage-gap default.
- **Fixture 10's auth response is inconsistent with its create response.**
  `gh auth status` reports a healthy login while `issue create` returns 403
  "Resource not accessible by integration". Possible with a fine-grained token,
  but nothing in the auth fixture hints at reduced scopes, so the trial had to
  infer the diagnosis. A `Token scopes:` line would make it verifiable.
- **Stub output shape differs from real `gh`.** `gh label list`,
  `gh milestone list` and `gh project list` return raw JSON without `--json`;
  real `gh` prints tables. A skill that parsed table output would pass here and
  fail in production.

## What holds up

The draft-and-approve contract is solid, which is the core of this skill. No
trial created an issue before its approval, across one-round (evals 1, 5, 7, 9,
10, 11), two-round (eval 4) and three-round (eval 8) sessions. The three
restraint evals produced zero creates between them, and did so again with the
leaked hints removed.

Honesty under failure is clean too. Eval 10's create returned 403 and the trial
said so in plain terms, named the likely cause, invented no issue number, and
offered concrete recovery. Eval 7 discovered that a user-requested label did not
exist, said so in the draft with three options, created with the valid label
only, and repeated the deviation in its closing message rather than letting the
user assume both labels landed.

## Measured before the milestone-command fix

These numbers were produced against the skill as it stood at the time of the run,
with Step 3 calling `gh milestone list` and the nine cassettes answering it. That
command and those fixtures changed immediately afterwards (a real `gh api ...
/milestones` call, cassettes re-keyed to match).

The results stand, and were spot-checked rather than assumed. The change alters
how milestones are fetched, not what comes back — both forms return
`v1.2 Release`, or `[]` for fixture 11 — so the information reaching each trial
is unchanged, and only eval 9's two milestone expectations touch the value at
all. Evals 1 and 9 were re-run against the fixed skill and fixtures: eval 1
behaved identically, and eval 9 still fails the same two expectations, which is
the one result that would have moved had the command mattered to grading.

Not re-measured: per-eval time, tokens and tool calls. Step 5's `mktemp` form is
marginally more work than the old fixed path, so those figures may drift by a
small amount the next time this suite runs.

## Notes

- with_skill only, no without_skill arm: `create-github-issue` is a workflow
  skill.
- Scripted user replies are embedded in each eval's prompt, which lets a
  single-shot executor play out a multi-turn approval session honestly. That is
  a better design than the interactive-ordering expectations that had to be
  reworded in the `pr` suite.
- Evals 5 and 8 grade body *content*, but `--body-file` means `gh-calls.log`
  records only a path and Step 8 deletes the file. Those two executors were asked
  to quote the body verbatim before cleanup so the content was gradeable from an
  artifact rather than from a summary.
