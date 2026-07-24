---
name: implement-feature
description: Implement a feature end-to-end — create a branch, implement it (optionally via sub-agents), commit early and often, open a draft PR, run an independent QA sub-agent review loop, mark the PR ready for review, then hand off to land-pr to reach a mergeable state. Use when the user asks to implement a feature and carry it through to a PR ready for review.
metadata:
  category: software-development
---

# Implement Feature

Take a feature from branch creation through to a PR that's ready for review and on its way to mergeable. This skill orchestrates existing skills rather than duplicating their logic — see **Skills Used** below.

## When to Use

- The user asks to implement a feature (or a well-scoped fix) and wants it carried through branch creation, implementation, commits, PR, independent QA, and merge-readiness monitoring in one pass.
- The user references this end-to-end flow explicitly (e.g. "implement X, have a QA agent check it, and get it ready for review").

## Skills Used

- `create-branch` — branch creation
- `commit` — commit message conventions
- `pr` — draft PR creation (marking ready for review is done directly via `gh pr ready` per step 7, bypassing the `pr` skill's update flow)
- `review-code` — optional, available to the QA sub-agent for a structured diff pass
- `land-pr` — drives the PR to a green, mergeable state after QA passes

Invoke each by name at the relevant step. Do not re-implement their instructions here — if a step feels underspecified, that skill has the detail.

## Instructions

### 1. Create the branch

If there's a linked Jira/GitHub issue, invoke the `create-branch` skill with the issue key and feature title. If there is no ticket, note that `create-branch`'s own instructions expect an issue key and don't define a keyless mode — don't hand it an empty key and expect a fallback that doesn't exist there. Instead, build the branch name directly (a slugified version of the feature name, following `create-branch`'s slugification and length conventions) and follow its remaining mechanics yourself: `git checkout -b <name>`, then check for an `origin` remote and connectivity before `git push -u origin <name>`. Skip its ticket-comment step, since there's no ticket to comment on.

### 2. Implement

- Break the work into pieces. If there are independent sub-tasks that don't share state (e.g. separate modules, a frontend/backend split, independent files), consider spawning sub-agents to implement them concurrently. This is a judgment call, not a requirement. As a tie-breaker: prefer sub-agents when there are 2+ independent files/modules with no shared state or overlapping edits; otherwise implement serially in the main thread. When sub-agents do run concurrently, use worktree isolation for them (or have the main thread serialize any git operations, like commits or installs, while they're active) to avoid working-tree races.
- Each sub-agent prompt must be self-contained: the feature goal, the specific slice it owns, relevant file paths, and how its output should integrate with the rest. Sub-agents start with no memory of this conversation or its history.
- If sub-agents are used, the main thread is responsible for integrating their output and resolving any conflicts between their changes before committing.

### 3. Commit early and often

Follow the `commit` skill's conventions. Commit logical chunks of work as they're completed rather than batching everything into one commit at the end.

### 4. Open the PR early

As soon as the first meaningful commit exists, invoke the `pr` skill to open a **draft** PR (the `pr` skill always creates drafts — never open one as ready-for-review at this stage). Continue implementing and committing to the same branch/PR as work continues.

### 5. Complete the implementation

Continue steps 2–4 until the feature is functionally complete and any relevant documentation (README, inline docs, comments) reflects the change.

### 6. QA review loop (max 3 rounds)

Repeat up to 3 rounds:

a. Spawn a **fresh-context sub-agent** instructed to act as a QA engineer. Its prompt must be self-contained, the same way step 2's implementation sub-agent prompts are: include the original feature request text (or a link to it), the PR number/branch, the relevant file paths, and — from round 2 onward — any issues pushed back on in a prior round together with the reasoning given, so this round's agent can independently concur with or reaffirm the original issue despite the rebuttal. The sub-agent has no memory of this conversation and nothing to judge against otherwise. Ask it to review the current implementation and its documentation against that request and list concrete issues — bugs, missed edge cases, doc/code mismatches, etc. It should not modify code itself — only report findings; fixing or pushing back is the main thread's responsibility. Tell it explicitly that it may invoke the `review-code` skill if a structured pass over the diff would help, but that this is an internal QA pass, not a human-facing review — it must tell `review-code` not to post to the PR, and instead return findings as text.

b. For each issue the QA agent raises, the main thread does one of:
   - **Fix it** — make the change, commit it (per step 3's conventions).
   - **Push back** — record the reasoning for why the issue doesn't apply or is out of scope. Since each round uses a fresh QA agent (step c), this reasoning isn't replied to in-place — carry it into the next round's QA prompt per step 6a.

c. If anything was fixed or pushed back on, run another round: spawn a **new fresh-context QA sub-agent** rather than continuing the prior one, so it evaluates the current state on its own merits instead of just reacting to the rebuttal.

d. Stop the loop when a round returns zero issues — none fixed, none pushed back on, none reaffirmed from a prior round — or when 3 rounds are complete, whichever comes first. A reaffirmed issue (one the QA agent raises again despite a prior round's pushback) still counts as an issue for this check; it is not "no new issues."

If the cap is hit while a disagreement is still unresolved (QA keeps raising something the main thread keeps pushing back on), stop and surface the specific disagreement to the user instead of forcing a resolution.

### 7. Mark ready for review

Once the QA loop is satisfied (or capped with no blocking disagreement), run `gh pr ready` directly. Don't route through the `pr` skill's full update flow — its assignee and title confirmation steps were already settled when the draft was opened in step 4.

### 8. Hand off to land-pr

Invoke the `land-pr` skill to drive the PR to a green, mergeable state — it handles PR comments, SonarQube findings, failing checks, and merge conflicts in its own loop. `land-pr` does not merge the PR.

### 9. Report

Summarize:

- Branch name and PR URL.
- Whether sub-agents were used for implementation, and for what.
- QA rounds run, what was fixed, and what was pushed back on (with reasoning).
- Final state handed back from `land-pr` (green/mergeable, or still blocked on specific items).

## Important Notes

- Do not mark the PR ready for review, or hand off to `land-pr`, until the QA loop has concluded (satisfied or capped).
- Sub-agents — implementation or QA — must be given the exact skill names they're allowed to invoke; they do not inherit awareness of this skill or its referenced skills from surrounding context.
- This skill never merges the PR. That remains a separate, explicit action.
