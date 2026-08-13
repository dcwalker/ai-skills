# ai-skills

Personal Claude Code plugins and skills, distributed as a plugin marketplace.

## Table of Contents

- [Plugins](#plugins)
- [Usage](#usage)
- [Installation](#installation)
- [Evals](#evals)
- [Contributing](#contributing)

## Plugins

- **life-skills** — Personal life-organization skills: `conduct-interview`, `organize-meeting-notes`, `triage`.
- **software-development** — Software development workflow skills: `analyze-logs`, `commit`, `create-branch`, `create-github-issue`, `fix-pr-checks`, `implement-feature`, `land-pr`, `pr`, `resolve-pr-comments`, `resolve-sonarqube-issues`, `review-code`, `review-readme`, `tidy-workspace`, `update-dependabot-bulk`.

## Usage

Once a plugin is installed, its skills activate in two ways:

- **Automatically**: describe what you want in conversation, and a skill whose
  description matches the request loads on its own (e.g. "commit these
  changes" triggers `commit`; "triage my inbox" triggers `triage`).
- **Explicitly**: invoke a skill by name as a slash command in the form
  `/<plugin>:<skill>`, optionally with arguments:

```text
/software-development:commit
/software-development:land-pr https://github.com/owner/repo/pull/42
/life-skills:triage
```

## Installation

Add this repo as a plugin marketplace in Claude Code:

```text
/plugin marketplace add dcwalker/ai-skills
```

Then install a plugin from it:

```text
/plugin install life-skills@dcwalker-skills
/plugin install software-development@dcwalker-skills
```

Run `/plugin` to browse installed and available plugins, or to update/remove one later.

### Claude Code on the web

The steps above cover a local install. A cloud session gets neither of them:
it clones the repository, but marketplace registrations and installed plugins
live in `~/.claude` on the machine where `/plugin` ran, so they do not travel.
`/plugin` is also unavailable in cloud sessions, leaving no in-session way to
add them. A fresh cloud session therefore reports `No plugins installed`, and
`/software-development:land-pr` comes back as an unknown command.

Install them from the cloud environment's **Setup script** instead, which runs
before Claude Code launches. Open the environment dialog at
[claude.ai/code](https://claude.ai/code) and set:

```bash
#!/bin/bash
claude plugin marketplace add dcwalker/ai-skills || true
claude plugin install life-skills@dcwalker-skills --scope user || true
claude plugin install software-development@dcwalker-skills --scope user || true
```

The `|| true` matters: a setup script that exits non-zero fails the session, so
a transient network error during install would cost you the session rather than
just the plugins. Claude Code snapshots the filesystem after the script
succeeds and reuses that snapshot, so the install runs once per environment
rather than once per session.

Two consequences worth knowing:

- The setup script belongs to the environment, not to this repository, so it
  applies to every repo you open in that environment and is lost if the
  environment is recreated. That is why it is written down here.
- Installing at `--scope user` deliberately leaves local sessions alone. The
  alternative, committing `extraKnownMarketplaces`/`enabledPlugins` to
  `.claude/settings.json`, would apply everywhere but project settings outrank
  user settings — so in this repository a committed marketplace would shadow a
  local checkout-based install and load the skills as published on the default
  branch. Editing a skill on a branch and then invoking it would run the
  pre-edit version, which is precisely the wrong behavior in the repository
  where these skills are authored.

## Evals

Every skill in this repo ships its own outcome-focused eval suite, following
[Anthropic's guide to evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents):
grade the final state a skill produced rather than the steps it took, include
both positive cases (clean scenario, the skill should act) and negative cases
(ambiguous scenario, the skill should ask or decline), and verify results
against ground truth instead of trusting the executor's self-report.

### How it works

- Each skill defines its cases in `plugins/<plugin>/skills/<skill>/evals/evals.json`
  (prompt, expected outcome, and gradeable expectations) with per-case fixtures
  under `evals/fixtures/<id>/`.
- Every trial runs in an isolated scratch environment. External systems are
  mocked at their natural seam: a fixture-driven fake `gh` CLI on `PATH` for
  GitHub-touching skills, opt-in fixture hooks for SonarQube and the Trello
  CLI script, and real protocol-compliant MCP stub servers (Trello, Gmail, Jira) for
  MCP-dependent skills, swapped in via `claude --strict-mcp-config`.
- An executor runs the skill against the trial's prompt; grading then checks
  the actual final state: files and git history, stub call logs, and final
  stub-state snapshots diffed against the seed.
- A small set of golden-path cases can run against a real disposable GitHub
  sandbox repo (gated by `EVAL_GH_SANDBOX_REPO`/`EVAL_GH_SANDBOX_TOKEN`; they
  skip cleanly when unset) to catch stub/reality drift.
- The `review-code` skill's skill-quality mode uses these suites for
  regression review: when a PR touches a skill, it runs static checks and, on
  explicit request, re-runs the skill's evals and diffs the results against
  the committed baseline.

### Where the results are

Each skill's committed baseline is the result of record: a human-readable
`benchmark-baseline.md` report (summary stats, per-eval pass rates, and notes
on every finding), with `benchmark-baseline.json` alongside it holding the
underlying data.

**life-skills:**
[conduct-interview](plugins/life-skills/skills/conduct-interview/evals/benchmark-baseline.md) ·
[organize-meeting-notes](plugins/life-skills/skills/organize-meeting-notes/evals/benchmark-baseline.md) ·
[triage](plugins/life-skills/skills/triage/evals/benchmark-baseline.md)

**software-development:**
[analyze-logs](plugins/software-development/skills/analyze-logs/evals/benchmark-baseline.md) ·
[commit](plugins/software-development/skills/commit/evals/benchmark-baseline.md) ·
[create-branch](plugins/software-development/skills/create-branch/evals/benchmark-baseline.md) ·
[create-github-issue](plugins/software-development/skills/create-github-issue/evals/benchmark-baseline.md) ·
[fix-pr-checks](plugins/software-development/skills/fix-pr-checks/evals/benchmark-baseline.md) ·
[implement-feature](plugins/software-development/skills/implement-feature/evals/benchmark-baseline.md) ·
[land-pr](plugins/software-development/skills/land-pr/evals/benchmark-baseline.md) ·
[pr](plugins/software-development/skills/pr/evals/benchmark-baseline.md) ·
[resolve-pr-comments](plugins/software-development/skills/resolve-pr-comments/evals/benchmark-baseline.md) ·
[resolve-sonarqube-issues](plugins/software-development/skills/resolve-sonarqube-issues/evals/benchmark-baseline.md) ·
[review-code](plugins/software-development/skills/review-code/evals/benchmark-baseline.md) ·
[review-readme](plugins/software-development/skills/review-readme/evals/benchmark-baseline.md) ·
[tidy-workspace](plugins/software-development/skills/tidy-workspace/evals/benchmark-baseline.md) ·
[update-dependabot-bulk](plugins/software-development/skills/update-dependabot-bulk/evals/benchmark-baseline.md)

Repo-wide: `python3 evals/lib/report.py` prints one table across every
committed baseline: per-skill eval counts, expectation pass rates, baseline
dates, and totals.

### How to run

- Most skills: `evals/lib/run-eval.sh <skill-evals-dir> <eval-id> <run-dir>`
  prepares an isolated trial (scratch repo, stubs on `PATH`, fixture env
  vars); the executor is then a Claude subagent pointed at the prepared
  workspace.
- MCP-backed skills (`triage`): trials must be real `claude -p` subprocesses,
  so run `bash plugins/life-skills/skills/triage/evals/run-trials.sh` from a
  logged-in terminal; it wires the MCP stubs via `evals/lib/run-mcp-eval.sh`
  and saves per-trial transcripts, call logs, final state, and metrics for
  grading.
- One-time setup for the MCP stubs (isolated venv):

  ```bash
  uv venv --python 3.11 evals/lib/mcp-stub/.venv
  uv pip install --python evals/lib/mcp-stub/.venv/bin/python3 -r evals/lib/mcp-stub/requirements.txt
  ```

Full details on the eval workflow, including the fixture and cassette formats
and how to add a new eval, are in [evals/README.md](evals/README.md).

## Contributing

Coding standards, testing expectations (including the eval requirements for
new and modified skills), and documentation guidelines are in
[CONTRIBUTING.md](CONTRIBUTING.md). Directives specific to AI coding agents
working in this repo are in [AGENTS.md](AGENTS.md).
