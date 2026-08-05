---
name: land-pr
description: Drive an already-open pull request to a green, mergeable state by looping through PR comments, SonarQube findings, failing checks, and merge conflicts. Use when the user wants a PR fully ready to merge, or asks to monitor a PR until it's mergeable. Does not merge the PR.
metadata:
  category: software-development
---

# Land PR

Drive an already-open pull request to a fully green, mergeable state. Loops through comment resolution, SonarQube findings, failing checks, and merge conflicts until nothing is left, or a round cap is hit. Stops short of merging — that remains a separate, explicit action.

## When to Use

- The user wants an open PR fully ready to merge.
- The user asks to monitor or babysit a PR until its checks pass.
- Called by another skill (e.g. `implement-feature`) once a PR is marked ready for review.

## Skills Used

This skill orchestrates rather than duplicates:

- `resolve-pr-comments` — unresolved PR review comments
- `resolve-sonarqube-issues` — SonarQube findings
- `fix-pr-checks` — failing CI checks
- `pr` — not invoked by this skill; if no PR exists, `land-pr` stops and reports that `pr` should be run first (see step 1)

Invoke each by name; do not re-implement their logic here.

## Instructions

Please start by reviewing the AGENTS.md and CONTRIBUTING.md files in the project (if present). Note any merge, rebase, or branch protection conventions that should override the defaults below.

### 1. Confirm the PR exists

```bash
gh pr view --json number,url,state,isDraft,mergeable,mergeStateStatus,statusCheckRollup,baseRefName,reviewDecision
```

If no PR exists for the current branch, stop and report — this skill assumes one is already open (use the `pr` skill first to create one).

If `isDraft` is true and this skill was invoked standalone (not as a hand-off from `implement-feature`, which only calls it after marking the PR ready), warn the user that GitHub's `mergeStateStatus` can be unreliable or report as unmergeable for draft PRs, and ask whether to proceed anyway or mark it ready first.

`baseRefName` from this call is `<base-branch>` in step 2a below. `reviewDecision` is used by the early-exit check in step 2f.

### 2. Loop until green (max 5 rounds)

Repeat the following round until `mergeable` is `MERGEABLE`, `mergeStateStatus` is `CLEAN`, and every check in `statusCheckRollup` is passing, or 5 rounds have run:

a. **Sync with the base branch.** Fetch the base branch and check for conflicts:
   ```bash
   git fetch origin <base-branch>
   git merge-tree --write-tree HEAD origin/<base-branch>
   ```
   A non-zero exit code means there are conflicts (this requires a git version supporting `--write-tree`; if unavailable, fall back to the three-arg form `git merge-tree "$(git merge-base HEAD origin/<base-branch>)" HEAD origin/<base-branch>` and grep its output for `<<<<<<<` conflict markers instead of relying on exit code). If conflicts are present, merge (or rebase, per this repo's convention) the base branch in, resolve conflicts, commit, and push. Never force-push without explicit user approval — even after confirming no one else has pushed to this branch — and never use `--no-verify` to bypass hooks.

b. **Resolve PR comments** — invoke the `resolve-pr-comments` skill if any unresolved comments exist.

c. **Resolve SonarQube findings** — invoke the `resolve-sonarqube-issues` skill if the SonarQube check reports outstanding issues. Note that skill runs its own internal scan-fix loop with no stated round cap of its own — it's the one step here that could run long before returning control. If it completes more than 3 scan-fix cycles without the issue count strictly decreasing, treat this round as stuck (not fixed) rather than waiting for it to converge.

d. **Fix failing checks** — invoke the `fix-pr-checks` skill for any other failing CI checks.

e. Re-run the `gh pr view` command from step 1 to refresh status before deciding whether another round is needed.

f. If, after a–d, nothing was found to fix (no comments, no SonarQube findings, no failing checks, no conflicts) but `mergeStateStatus` is still not `CLEAN`, check `reviewDecision`: if it's `REVIEW_REQUIRED` (or similar — the PR is blocked purely on a human approval gate none of the four sub-steps can satisfy), stop looping immediately rather than burning the remaining rounds, and report that the PR is waiting on review approval.

Log a one-line summary after each round: what was fixed, what's still outstanding.

### 3. Round cap

If 5 rounds complete and the PR is still not green, stop looping. Report exactly what remains outstanding (which checks, which comments, which conflicts) and ask the user how to proceed rather than continuing indefinitely. This mirrors `fix-pr-checks`' own "stop after repeated failures" rule — a persistent failure after several rounds usually needs a decision only the user can make (e.g. the check itself is misconfigured, or the fix requires an out-of-scope change). If `isDraft` was (or still is) true, repeat the step 1 caveat that `mergeStateStatus` can be unreliable for draft PRs — that may be the actual reason nothing read as green.

### 4. Report

Summarize:

- Rounds run and what each resolved (comments, SonarQube issues, checks, conflicts).
- Final PR state: green and mergeable, or still blocked with specific remaining items.
- The PR as a clickable link — `[#501](https://github.com/<owner>/<repo>/pull/501)`, using the `url` field `gh pr view` returned, not a bare `#501`. Link every remaining blocked item the same way (a failing check to its check-run URL, an unresolved comment to its comment URL) so the user can go straight to it. Only use URLs `gh` actually returned; if an item came back without one, name it in plain text rather than constructing a URL.

## Important Notes

- **Never merges the PR.** Merging affects shared state and requires separate, explicit approval — this skill's job ends at "green and mergeable."
- Never force-pushes without explicit user approval, and never bypasses hooks with `--no-verify`.
- If the same check or comment keeps failing after being "fixed," treat that as a sign the fix is wrong rather than re-attempting the same change — stop and ask.
