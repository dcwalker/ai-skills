---
name: tidy-workspace
description: Clean up a repo after coding work is done — remove worktrees, resolve uncommitted files, clean up stale stashes, sync the main branch, delete merged branches, and update worked-on issues. Use when the user asks to tidy up, clean up, or wrap up after finishing work in a repo.
metadata:
  category: software-development
---

# Tidy Workspace

Clean up a git repository and its associated issues after a round of coding work is finished. This skill builds one consolidated plan up front, gets a single approval, then executes every step. It does not ask again mid-run — get the plan right before proceeding.

## When to Use

Use this skill when:
- The user asks to tidy up, clean up, or wrap up after finishing work.
- A coding session is done and local state (worktrees, branches, uncommitted files) needs to be reset to a clean baseline.

## Instructions

Please start by reviewing the AGENTS.md and CONTRIBUTING.md files in the project (if present). Note any branch naming, gitignore, or issue-tracker conventions that should override the defaults below.

### 1. Gather current state (read-only, no changes yet)

- `git worktree list` — every worktree and its branch.
- `git status --porcelain=v1 -uall` — every unstaged, staged, and untracked file.
- `git stash list` — every stash. For each one, gather what is needed to judge
  whether it is still relevant: the stashed diff (`git stash show -p stash@{N}`),
  the branch it was created on and when (from the stash's own subject line and
  `git log -g refs/stash`), and any issue key or PR reference derivable from that
  branch name or the stash message. Then evaluate it against the project's
  history: has equivalent or conflicting work already landed on the main branch
  (compare the stashed hunks against the current file contents, and use
  `git log -S "<distinctive snippet>"` to find commits touching the same code)?
  Was the related work abandoned (source branch deleted, tracked issue closed as
  won't-fix or done without these changes)? Check the tracking tool the repo
  actually uses, whether that is GitHub issues/PRs, Jira, or something else,
  using the same lookup tools as the issues bullet below. Classify each stash as
  *superseded* (equivalent change already merged), *abandoned* (the work it
  belongs to is closed or discarded), *still relevant* (belongs to live work),
  or *unclear*. Only a confident superseded/abandoned classification may be
  proposed as a drop; anything unclear gets asked about, not guessed at.
- If a remote exists, fetch and prune it first (e.g. `git fetch --prune`), before computing anything merge- or branch-related below. Otherwise later checks can read a stale local view — missing branches the remote already deleted on merge, or wrongly reporting a genuinely-merged branch as unmerged.
- Determine the main branch: `gh repo view --json defaultBranchRef` if a GitHub remote exists, else `git remote show origin | grep 'HEAD branch'`, else fall back to `main` or `master` (whichever exists).
- Compute the **ancestry-merged** list — `git branch --merged` and `git branch -r --merged` — against the remote-tracking ref for main (e.g. `origin/<main>`) if a remote exists, not the local `<main>` branch: local `<main>` may not be fetched/pulled to the latest merged state yet, and checking a stale local main can wrongly report a genuinely-merged branch as unmerged. Fall back to local `<main>` only when there's no remote to check against.
- `git branch --merged` only catches fast-forward/true merges. Also cross-check squash- or rebase-merged branches with `gh pr list --state merged --json headRefName` (or the equivalent Jira/Bitbucket check if not GitHub) so branches merged via squash aren't missed. Keep any branch found here that is *not* already in the ancestry-merged list as its own list — call it **PR-state-merged**. This distinction matters for deletion in step 4: a squash/rebase-merged branch's commits are never an ancestor of the main branch, so a plain ancestry check (and `git branch -d`) will always report it as unmerged even though GitHub confirms the PR merged.
- Exclude protected branches from any deletion candidate list: the main branch itself, plus common long-lived names if present (`master`, `main`, `develop`, `staging`, `production`), plus anything checked out in a worktree (handle those under step for worktrees instead).
- Identify issues worked on this session: scan the current conversation for issue keys, ticket numbers, or PR/branch references (e.g. `PROJ-123`, `#456`), and cross-reference with local branch names and recent commit messages (`git log --oneline <main>..HEAD` per relevant branch). Look up each one's current status via `gh issue view <n>` / `gh pr view <n>` or `acli jira workitem view <key>`. If the repo has no separate issue tracker — no ticket references in branch names, commit messages, or the conversation, and no linked issues on the PR — treat the pull/merge request itself as the unit of tracked work and mark this section N/A in the plan rather than searching further.

### 2. Build one consolidated plan — do not act yet

Present a single plan to the user covering everything below, then wait for one approval before touching anything:

- **Worktrees to remove**: path and branch for each. Flag any worktree with uncommitted or unpushed changes explicitly — do not silently include a force-remove for these; call them out so the user can decide.
- **Uncommitted/unstaged files**: for each file or logical group, propose one of:
  - *Commit* — file belongs in the repo; propose which commit/message it should go into.
  - *Delete* — scratch/debug output not needed.
  - *Gitignore* — should be kept on disk but not tracked; propose the `.gitignore` entry.
  Give a brief reason for each recommendation.
- **Stashes to clean up**: for each stash from step 1, list its index, source
  branch, age, a one-line summary of what it contains, and its classification
  with the evidence (the merged commit that supersedes it, the closed issue or
  deleted branch that abandons it, or the live work it belongs to). Propose
  *drop* only for confident superseded/abandoned classifications. Propose
  *keep* for still-relevant stashes. For any stash classified *unclear*, or
  where the evidence is thin, present it as an explicit question in the plan
  (with options: keep, drop, or apply to a branch now) rather than folding it
  into the blanket approval; a stash is unrecoverable once dropped, so low
  confidence always goes to the user.
- **Branch sync**: confirm target is the main branch (from step 1) and that it will be pulled after checkout.
- **Merged branches to delete**: local and remote, from the filtered lists in step 1 (protected and checked-out branches excluded). List them explicitly rather than deleting by wildcard, and note which were ancestry-merged vs. PR-state-merged only, since that determines `-d` vs `-D` in step 4.
- **Issues to update**: each issue/ticket identified, its current status, and the proposed new status/comment (e.g. mark done, add a closing comment, link the merged PR) — or N/A per step 1, if the repo has no separate issue tracker.

### 3. Wait for approval

Do not proceed past the plan without explicit confirmation. If the user asks for changes to the plan, revise and re-present before executing. Once approved, run all steps below without pausing for further per-step confirmation.

### 4. Execute

1. **Remove worktrees**: `git worktree remove <path>` for each approved entry. Only use `--force` for entries the user explicitly approved despite uncommitted/unpushed changes.
2. **Resolve uncommitted files** per the approved plan:
   - Commits: stage and commit following this project's commit conventions (reuse the `commit` skill's message format if unsure).
   - Deletions: remove the files.
   - Gitignore: add entries to `.gitignore` and, if the files are currently tracked, `git rm --cached` them.
3. **Switch and sync**: `git checkout <main>` then `git pull`.
4. **Delete merged branches**, per branch:
   - **Ancestry-merged** (from `git branch --merged`): `git branch -d <branch>` locally — if this fails, the branch is not actually merged; stop and flag it rather than forcing.
   - **PR-state-merged only** (confirmed via `gh pr list --state merged` but not ancestry-merged, e.g. squash/rebase merges): `git branch -d` will always fail for these since the commits are never an ancestor of the main branch. Use `git branch -D <branch>` instead — the merge status was already verified against GitHub/Jira, not local ancestry.
   - Remote, for both categories: check `git rev-parse --verify --quiet origin/<branch>` (relying on the fetch/prune from step 1, no extra network call needed) before deleting. If it resolves, `git push origin --delete <branch>`; if it's already gone — many hosts can auto-delete the source branch on merge — skip it and note that in the report instead of attempting a delete that will just fail.
5. **Drop approved stashes**: `git stash drop stash@{N}` for each stash
   approved for dropping, processing from the highest index to the lowest so
   earlier drops do not renumber the remaining ones. Never drop a stash the
   plan classified as unclear unless the user explicitly resolved it; if the
   user chose *apply to a branch now* for a stash, apply it there first and
   only drop once the apply succeeds cleanly.
6. **Update issues**: for each approved issue, post the status update/comment via `gh issue`/`gh pr` or `acli jira workitem` as appropriate.

### 5. Report

Summarize what was done:
- Worktrees removed (and any skipped/flagged).
- Files committed, deleted, or gitignored.
- Stashes dropped (with the classification that justified each), kept, or
  left pending a user decision.
- Branch checked out and pull result.
- Branches deleted locally and remotely, any skipped because they weren't actually merged, and any remote branches skipped because they were already deleted (e.g. by the host's auto-delete-on-merge).
- Issues updated and their new status.

If any step fails, stop, report the error, and ask how to proceed rather than continuing to the next step.
