---
name: review-code
description: Reviews local code or a pull request against repository-specific guidelines. Loads CONTRIBUTING.md as the primary standard, supplements with AGENTS.md and any tool-specific instruction files found in the repo. For PRs, auto-detects the open PR, reviews the actual diff, and posts the review to the PR as inline comments and a summary by default (unless told not to). Use when asked to review a PR, review code changes, or do a code review.
metadata:
  category: software-development
---

# Code Review

Reviews code against repository-specific guidelines with the thoroughness of an experienced software tester.

This skill runs both **interactively** and **unattended** (e.g. from CI against a
pull request). Never block waiting for input: auto-detect the context, apply the
defaults below, and act. Treat anything the invoking request says as an override
of those defaults.

## Step 1: Determine the target and destination

Detect whether the current branch has an open PR:
```bash
gh pr view --json number,title,url,headRefName 2>/dev/null
```

**What to review (do not ask):**
- If a PR is found for the branch, review that PR (its diff and changed files).
- If no PR is found, review the local working tree.
- Override only when the request says so — e.g. "review my local changes" even
  though a PR exists, or a specific PR number/URL to review instead.

**Where the review goes (do not ask):**
- If a PR exists for the branch, post the review directly to that PR as inline
  comments and a summary (Step 5 → "Post the review to the PR").
- If no PR exists, output the review as text (Step 5 → "Text output").
- When a PR exists, fall back to text only if the request explicitly opted out of
  posting (e.g. "just show me the text," "don't post to the PR").

## Step 2: Load guidelines

**Primary** — read the first one found:
- `CONTRIBUTING.md`
- `CONTRIBUTING.rst`
- `docs/CONTRIBUTING.md`
- `.github/CONTRIBUTING.md`

**Neutral AI instructions** — read if found:
- `AGENTS.md`

**Tool-specific** — scan and read any that exist:
- `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursorrules`, `.cursor/rules/*.mdc` (use Glob), `.windsurfrules`, `.clinerules`, `DEVIN.md`

Track which sources were loaded — include them in the output.

If none are found, do **not** skip: review against general software-engineering
and security best practices instead, and note in the output that no repo-specific
guidelines were found (see Step 5 → "No repo-specific guidelines").

## Step 3: Get the code to review

**Local mode:** Read files from disk with `Read`, `Glob`, `Grep`.

**PR mode:** `gh` infers the PR number, owner, and repo from the checked-out
branch, so no IDs need to be supplied by hand. Do NOT assume local files match
the PR. Get the diff and metadata:
```bash
gh pr diff <number>
gh pr view <number> --json title,body,headRefName,baseRefName,author,additions,deletions,changedFiles,commits,headRefOid
```
Read each changed file in full using `Read`. If the local file does not match the PR's head (e.g. a different branch is checked out), fetch from the PR's head ref:
```bash
gh api repos/{owner}/{repo}/contents/{path}?ref={headRefOid} --jq '.content' | base64 -d
```

## Step 4: Review

**Thoroughness over speed.** Read every changed file in full — do not rely solely on the diff. Trace logic across the codebase: follow function calls, check callers, examine related files not in the diff but affected by the changes.

Question every implementation decision with a tester's mindset:
- What assumptions does this code make? Are they documented or enforced?
- What happens at boundary conditions — empty input, nulls, max values, concurrent access?
- How does it behave in failure modes — network failures, slow DB, unexpected upstream data?
- Is the happy path tested? Are the unhappy paths tested?
- Does the change introduce or leave open any security surface (input validation, auth checks, data exposure)?
- Are there race conditions, missing locks, or shared mutable state?
- Is the abstraction right — is this code doing too much or too little?

Use `Grep` to understand how changed code is used elsewhere before deciding whether to flag something.

Assign a risk score 0–100 based on the most serious issue found:

| Score | Risk | Meaning |
|-------|------|---------|
| 0–19 | 🟢 None | No issues |
| 20–39 | 🟢 Low | Minor style or convention issues |
| 40–59 | 🟡 Medium | Missing best practices, incomplete work |
| 60–79 | 🔴 High | Correctness concerns, unsafe patterns |
| 80–100 | 🔴 Critical | Will break in production, security vulnerabilities |

## Step 5: Output

### Text output

Use this format when there is no PR to post to (local review), or when posting was explicitly opted out:

```
=== Code Review ===

Repository:    owner/repo
Branch:        feature/my-changes        (PR mode only)
PR:            #42 — My PR title         (PR mode only)
Guidelines:    CONTRIBUTING.md, AGENTS.md
Risk Score:    35/100 🟡 Medium

=== Issues ===

Found 3 issues

File: src/api.ts
---
Line:          42
Risk:          🔴 High (60)
Issue:
| Missing null check before accessing user.id. This will throw a TypeError
| if user is undefined — possible when the session expires mid-request.
| Suggestion: const id = user?.id ?? throwError('No user in session')

File: src/service.ts
---
Risk:          🟡 Medium (40)
Issue:
| Error handling is missing from the catch block per CONTRIBUTING.md §4.
| Silently swallowing errors here makes failures invisible in production.

PR Level
---
Risk:          🟢 Low (0)
Note:
| Guidelines loaded: CONTRIBUTING.md, AGENTS.md

=== Summary ===

Risk Score:    35/100
Issues:        3
  🔴 High:     1
  🟡 Medium:   1
  🟢 Low:      1
```

Wrap issue text at ~80 characters and prefix each line with `| ` (matching the sonar script style). Risk emoji: 🔴 for score ≥ 60, 🟡 for 40–59, 🟢 for < 40.

### Post the review to the PR

**Posting is the default when a PR exists for the branch** (Step 1) — post
without asking. Skip posting only if the user has explicitly opted out, in which
case use text output instead.

Post the review using **whatever PR-review capability your environment provides**
— your runtime's native PR-commenting tool when one is available, otherwise `gh`.
Do not hard-code a specific posting command. The review is made up of:

- **Inline comments** on the specific changed lines — each concise and actionable,
  with a suggested fix where possible. Only comment on lines present in the PR
  diff; PR-level observations belong in the summary.
- **A summary** stating the overall risk (none / low / medium / high / critical)
  and the standards you reviewed against.
- **A verdict, only if your environment supports submitting one:**
  `REQUEST_CHANGES` when any finding is High or Critical (≥ 60, 🔴); `APPROVE`
  when there is nothing worth commenting on; `COMMENT` otherwise. If verdicts
  aren't available, convey the same outcome in the summary.

After posting, output the review URL if one is available.

### No repo-specific guidelines

If no guideline files were found (Step 2), still perform the review against
general software-engineering and security best practices. Add a note to the
output / PR summary so the reader knows the basis:

> No repo-specific guideline files (CONTRIBUTING.md, AGENTS.md, …) were found;
> reviewed against general engineering and security best practices. Add a
> CONTRIBUTING.md to tailor future reviews.

## Rules

- Run end-to-end without interactive prompts: detect the target, apply the Step 1 defaults, and act. Honor explicit instructions in the request as overrides
- In PR mode, verify you are reviewing the correct code using the PR diff — do not assume local state matches
- When a PR exists for the branch, post the review to that PR by default; skip posting only if the request explicitly opted out
- If your environment supports a review verdict, set it by outcome: `REQUEST_CHANGES` for High/Critical risk (≥ 60, 🔴), `APPROVE` when there is nothing worth commenting on, otherwise `COMMENT`; if not, convey the outcome in the summary
- Never skip the review for lack of guideline files — fall back to general best practices (Step 2)
- Posting requires the runtime to have pull-request write permission (via a native PR-commenting tool or `gh`); this is a workflow/credential concern, not something to prompt about
- Do not use the `Write` tool
- Allowed tools: `Read`, `Glob`, `Grep`, `Bash` (for `gh` commands only)
