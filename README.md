# ai-skills

Personal Claude Code plugins and skills, distributed as a plugin marketplace.

## Plugins

- **life-skills** — Personal life-organization skills: `conduct-interview`, `organize-meeting-notes`, `triage`.
- **software-development** — Software development workflow skills: `analyze-logs`, `commit`, `create-branch`, `create-github-issue`, `fix-pr-checks`, `implement-feature`, `land-pr`, `pr`, `resolve-pr-comments`, `resolve-sonarqube-issues`, `review-code`, `review-readme`, `tidy-workspace`, `update-dependabot-bulk`.

## Installation

Add this repo as a plugin marketplace in Claude Code:

```
/plugin marketplace add dcwalker/ai-skills
```

Then install a plugin from it:

```
/plugin install life-skills@dcwalker-skills
/plugin install software-development@dcwalker-skills
```

Run `/plugin` to browse installed and available plugins, or to update/remove one later.

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
  CLI script, and real protocol-compliant MCP stub servers (Trello, Gmail) for
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

- Per skill: `plugins/<plugin>/skills/<skill>/evals/benchmark-baseline.md` is
  the human-readable report (summary stats, per-eval pass rates, and notes on
  every finding), with `benchmark-baseline.json` holding the underlying data.
  These committed baselines are the results of record.
- Repo-wide: `python3 evals/lib/report.py` prints one table across every
  committed baseline: per-skill eval counts, expectation pass rates, baseline
  dates, and totals.

### How to run

- Most skills: `evals/lib/run-eval.sh <skill-evals-dir> <eval-id> <run-dir>`
  prepares an isolated trial (scratch repo, stubs on `PATH`, fixture env
  vars); the executor is then a Claude subagent pointed at the prepared
  workspace. See `evals/README.md` for the full workflow.
- MCP-backed skills (`triage`): trials must be real `claude -p` subprocesses,
  so run `bash plugins/life-skills/skills/triage/evals/run-trials.sh` from a
  logged-in terminal; it wires the MCP stubs via `evals/lib/run-mcp-eval.sh`
  and saves per-trial transcripts, call logs, final state, and metrics for
  grading.
- One-time setup for the MCP stubs (isolated venv):

  ```
  uv venv --python 3.11 evals/lib/mcp-stub/.venv
  uv pip install --python evals/lib/mcp-stub/.venv/bin/python3 -r evals/lib/mcp-stub/requirements.txt
  ```

Full details, including the fixture and cassette formats and how to add a new
eval, are in [evals/README.md](evals/README.md).
