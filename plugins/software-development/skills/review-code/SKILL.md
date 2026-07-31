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

**Skill-quality mode (additive, do not ask):** if the diff touches any
`SKILL.md`, `evals/evals.json`, `evals/benchmark-baseline.*`, or other file
under a `plugins/*/skills/<skill>/` path, ALSO run Step 4b (Skill Quality
Review) for each affected skill. General code review still applies to every
file in the diff, including the skill files themselves.

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

**Mixed diffs (code + skills):** a diff that touches both ordinary code and
skill files gets both treatments — every file goes through this step's normal
review, and each affected skill additionally goes through Step 4b. Neither
substitutes for the other: a bug in a skill's bundled script is a Step 4 code
finding AND may also be a Step 4b resource-organization finding.

Assign a risk score 0–100 based on the most serious issue found — across
Step 4 and Step 4b findings alike; a single scale covers both:

| Score | Risk | Meaning |
|-------|------|---------|
| 0–19 | 🟢 None | No issues |
| 20–39 | 🟢 Low | Minor style or convention issues |
| 40–59 | 🟡 Medium | Missing best practices, incomplete work |
| 60–79 | 🔴 High | Correctness concerns, unsafe patterns |
| 80–100 | 🔴 Critical | Will break in production, security vulnerabilities |

## Step 4b: Skill Quality Review

Runs in addition to Step 4, only for skills the diff touches (see Step 1).
It has a cheap static part that always runs, and an expensive dynamic part
that runs **only on explicit request**.

### Static checks (always)

For each affected skill, check and report:

- **Description quality**: the frontmatter `description` states what the skill
  does AND when to use it, with concrete triggering phrases — the description
  is the only thing the model sees when deciding whether to load the skill.
- **Line budget / progressive disclosure**: SKILL.md under ~500 lines; large
  reference material split into `references/` files rather than inlined.
- **Naming convention**: lowercase-hyphen name; action skills follow
  `{intent}-{subject}[-{qualifier}]`, integrations `{tool}[-{scope}]`. Reuse
  the intent words already established by sibling skills (no synonym drift,
  e.g. mixing `fix`/`resolve` for the same intent). If
  `~/rules/skill-naming-conventions.md` exists in this environment, apply it
  as the authority; otherwise apply the pattern above as observed from the
  existing skill set.
- **Bundled-resource organization**: `scripts/`, `references/`, and `evals/`
  subdirectories follow this repo's existing layout; any script SKILL.md
  references actually exists in the repo (a referenced-but-missing bundled
  script is a High finding — it has happened here before).
- **Eval hygiene**: if the skill has `evals/evals.json`, the eval set includes
  both positive and negative cases, and fixture directories referenced by the
  evals exist. If the diff changes `evals.json` or fixtures without updating
  `benchmark-baseline.*`, flag that the baseline may be stale.

### Dynamic check (only on explicit request)

Running a skill's evals spawns executor and grader subagents per eval — slow
and costly. **Do not run evals by default, and never in an unattended/CI run
unless the invoking request explicitly asks** (e.g. "run the evals", "check
the benchmark" in the request or a `/re-review` comment body). When not
requested, add one line to the Skill Quality section: evals not run; the
checked-in `benchmark-baseline.*` is the last verified result.

When explicitly requested:

1. Run the changed skill's evals via the executor/grader flow this repo's
   baselines were built with (see `evals/README.md`; use `evals/lib/run-eval.sh`
   per trial, or `evals/lib/run-mcp-eval.sh` for MCP-backed skills — noting the
   latter requires a real `claude -p` subprocess, which not every environment
   can authenticate).
2. Aggregate results and diff against the skill's checked-in
   `evals/benchmark-baseline.json`: flag pass-rate drops and newly-failing
   expectations (each at minimum a Medium finding; treat a drop on a
   previously-100% eval as High), and note material time/token regressions
   and improvements.
3. Verify results against ground truth (fixture logs, final state), not
   executor self-report — the same rule the baselines follow.

For the dynamic check only, the `Agent` tool and unrestricted `Bash` are
permitted, as exceptions to the Rules below. The static checks stay within
the standard allowed tools.



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

=== Skill Quality ===              (only when the diff touches skill files)

Skill: triage (plugins/life-skills/skills/triage)
---
Static checks:  description ✓ · line budget ✓ (699 — over ~500, flag) ·
                naming ✓ · resources ✓ · eval hygiene ✓
Evals:          not run (on-request only); baseline of record:
                evals/benchmark-baseline.json (83.3% pass, 2026-07-31)

Skill: commit (plugins/software-development/skills/commit)
---
Static checks:  all ✓
Evals:          run on request — see table below

| Eval | Baseline | This run | Δ |
|------|----------|----------|---|
| 1    | 4/4      | 4/4      | = |
| 2    | 4/4      | 3/4      | ▼ newly failing: "commit message references the issue" |

=== Summary ===

Risk Score:    35/100
Issues:        3
  🔴 High:     1
  🟡 Medium:   1
  🟢 Low:      1
```

In a mixed diff, the Issues section covers all files (code and skill files
alike) and the Skill Quality section appears additionally, once per affected
skill. Skill-quality findings count toward the issue totals and the risk
score like any other finding.

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
  and the standards you reviewed against. When the diff touches skill files,
  include the Skill Quality section (static-check results per affected skill,
  and the eval-vs-baseline table when evals were explicitly requested) in this
  summary comment, above the risk marker.
- **A verdict, only if your environment supports submitting one:**
  `REQUEST_CHANGES` when any finding is High or Critical (≥ 60, 🔴); `APPROVE`
  when there is nothing worth commenting on; `COMMENT` otherwise. If verdicts
  aren't available, convey the same outcome in the summary.
- **A machine-readable risk marker**, as the very last line of the summary
  comment, in exactly this format: `RISK-LEVEL: <BAND>`, where `<BAND>` is the
  risk band from the table above in uppercase (`NONE`, `LOW`, `MEDIUM`, `HIGH`,
  or `CRITICAL`) matching the score you assigned. This is plain visible text,
  not a hidden HTML comment — some CI environments running this skill parse
  this exact line to apply a risk-level label to the PR automatically, and it
  must survive whatever sanitizes the posted comment, so it cannot rely on
  markup that gets stripped. Always include it exactly once, as the last line
  with nothing after it, even when the risk is `NONE`. Use this exact label
  (`RISK-LEVEL:`, distinct from the more conversational "Risk Level" wording
  elsewhere in the summary) so a parser can find this one unambiguously.

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
- Exception, scoped to Step 4b's dynamic check only (and only when evals were
  explicitly requested): the `Agent` tool (executor/grader subagents) and
  `Bash` beyond `gh` (eval harness scripts). Everything else in the review,
  including all static skill-quality checks, stays within the standard
  allowed tools above
