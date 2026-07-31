# Eval harness

Shared infrastructure for skill evals across both plugins in this repo. Individual
skills' eval definitions live next to the skill (`plugins/<plugin>/skills/<skill>/evals/`),
in the schema `skill-creator` expects (`evals.json` with `id`, `prompt`,
`expected_output`, `expectations`, optional `files`) so the standard
skill-creator executor/grader/benchmark workflow runs them directly. This
directory holds the plumbing every skill's evals share: an isolated scratch
git repo per trial, and a fake `gh` CLI so GitHub-touching skills can be
evaluated offline and deterministically.

See the top-level guide this harness follows: outcome-focused grading (judge
what the skill produced, not the exact steps it took), balanced positive and
negative cases, isolated per-trial state, and graders combining code-based
checks with model-based judgment where the outcome is inherently subjective.

## Layout

```
evals/
├── lib/
│   ├── gh-stub/gh       Fake `gh` executable, fixture/cassette-driven.
│   ├── git-fixture.sh   Builds a scratch git repo from a fixture spec.
│   ├── run-eval.sh      Per-eval harness: wires fixture + gh-stub + env vars.
│   └── sandbox/check.sh Gate for the small set of live sandbox-repo cases.
└── README.md            This file.

plugins/<plugin>/skills/<skill>/evals/
├── evals.json                 Eval definitions (skill-creator schema).
├── benchmark-baseline.json    Last-approved benchmark.json snapshot; the
│                              reference point review-code diffs against.
└── fixtures/
    └── <eval-id>/
        ├── repo/              Working tree to seed as the initial commit.
        ├── setup.sh           Optional: create extra branches/commits.
        ├── meta.json          Optional: {"checkout": "<branch>"}.
        ├── gh-cassette.json   Optional: canned `gh` responses for this eval.
        ├── sonar-fixture.json Optional: canned Sonar API responses.
        └── sonar-project-key Optional: plain-text project key, exported as
                               SONAR_PROJECT_KEY when sonar-fixture.json is
                               present -- lets a fixture skip shipping a
                               sonar-project.properties file in repo/.
```

## Running one eval trial

```bash
source "$(evals/lib/run-eval.sh plugins/software-development/skills/commit/evals 3 /tmp/eval-run)"
cd "$WORKSPACE_DIR"
# ... spawn the executor subagent here, pointed at $WORKSPACE_DIR with the
# skill loaded and PATH/GH_STUB_CASSETTE/SONAR_FIXTURE_FILE already exported ...
```

`run-eval.sh` only prepares the environment -- it doesn't run the skill. The
executor is a Claude subagent (per skill-creator's model), not a script, so
spawning it is the orchestrating agent's job: point the subagent at
`$WORKSPACE_DIR` as its cwd and hand it the eval's `prompt` from `evals.json`.

Teardown is just `rm -rf /tmp/eval-run` -- there's no separate script.

## The `gh` stub

Set `GH_STUB_CASSETTE` (done automatically by `run-eval.sh` when
`fixtures/<eval-id>/gh-cassette.json` exists) and prepend `evals/lib/gh-stub`
to `PATH`. Every `gh <args>` call is matched against the cassette's `calls`
list by substring or regex against the joined argv -- **not** by strict call
order, so a skill that reaches the same outcome through a different sequence
of `gh` invocations still passes. An unmatched call fails loudly with the
attempted argv, so a fixture gap is obvious immediately rather than silently
returning empty data that makes a grader guess wrong.

Every invocation is also appended to `GH_STUB_LOG` (one JSON line per call,
set automatically by `run-eval.sh`), so a grader can assert on what was or
wasn't called -- e.g. "no `pr merge` call happened," "`pr create` was called
with `--draft`" -- without constraining the exact path taken to get there.

See the docstring at the top of `lib/gh-stub/gh` for the full cassette
format.

## The Sonar fixture hook

`resolve-sonarqube-issues`'s bundled script reads `SONAR_FIXTURE_FILE` (an
opt-in env var; unset in normal use, so production behavior is untouched) and
serves canned JSON instead of calling a real SonarQube server. `run-eval.sh`
sets it automatically when `fixtures/<eval-id>/sonar-fixture.json` exists,
along with dummy `SONAR_HOST_URL`/`SONAR_TOKEN` values (never used for real
network calls in fixture mode). If `fixtures/<eval-id>/sonar-project-key`
also exists, its contents are exported as `SONAR_PROJECT_KEY`, so the fixture
repo doesn't need a `sonar-project.properties` file just to satisfy the
script's project-key lookup.

## MCP stub servers (Trello)

`triage` depends on real MCP tools (Trello today; Jira/Gmail may follow the
same pattern later) rather than a CLI on `PATH`, so it needs a different
mocking seam than `gh`/Sonar. `evals/lib/mcp-stub/` holds real,
protocol-compliant MCP stdio servers (built on the official `mcp` Python SDK,
not a hand-rolled JSON-RPC shim) that stand in for the real third-party
server -- `trello_stub.py` implements the subset of Trello tools `triage`
actually calls, backed by an in-memory fake "database" seeded from a fixture
file. Tool names and parameter schemas were confirmed against a live
connected Trello MCP server, not guessed from prose, so a skill's real tool
calls (including name-based list/board resolution and `update_card`'s batch
form) match the stub instead of silently no-oping.

Requires a one-time local dependency install (isolated venv, not system
Python -- see `evals/lib/mcp-stub/requirements.txt`):

```bash
uv venv --python 3.11 evals/lib/mcp-stub/.venv
uv pip install --python evals/lib/mcp-stub/.venv/bin/python3 -r evals/lib/mcp-stub/requirements.txt
```

**Mechanical difference from every other skill's evals:** MCP server
resolution happens once when a `claude` process starts -- unlike `PATH`,
which a subagent's Bash calls can pick up per-command via a sourced
`env.sh`. So a `triage` eval's executor must be a real, separate `claude`
CLI subprocess (launched via `claude -p --strict-mcp-config --mcp-config
...`), not an `Agent`-tool subagent like the other 15 skills use.

```bash
source "$(evals/lib/run-mcp-eval.sh plugins/life-skills/skills/triage/evals 1 /tmp/eval-run)"
cd "$WORKSPACE_DIR"
claude -p --dangerously-skip-permissions \
  --strict-mcp-config --mcp-config "$MCP_CONFIG_PATH" \
  -- "<the eval's prompt from evals.json>"
```

`run-mcp-eval.sh` wires a fixture's `trello-mcp-state.json` (the stub's seed
state) into a scratch `mcp-config.json` naming the stub as the *only* MCP
server, so the real Trello MCP server is never reachable during a trial.
After the trial, grade by diffing `$MCP_STUB_STATE_OUT` (final state) against
an expected snapshot, and/or reading `$MCP_STUB_LOG` (one JSON line per tool
call) -- the same "grade final state, not exact steps" philosophy as every
other eval in this repo, not by trusting the subprocess's stdout self-report.

## Live sandbox cases

A handful of "golden path" evals per GitHub-touching skill are marked
`"sandbox": true` in `evals.json` and run against a real disposable GitHub
repo instead of the stub, to catch stub/reality drift. They need
`EVAL_GH_SANDBOX_REPO` (`owner/repo`) and `EVAL_GH_SANDBOX_TOKEN` set to a
token scoped to that repo only -- **never point this at a real project
repo**, these evals create and mutate PRs/issues/branches as part of normal
operation. Check `lib/sandbox/check.sh` before running one; it exits `77`
(skip, not fail) when the sandbox isn't configured, so the rest of the suite
runs fine without it.

## Adding a new eval

1. Add an entry to the skill's `evals.json` (id, prompt, expected_output,
   expectations).
2. Create `fixtures/<eval-id>/` with whatever the scenario needs: a `repo/`
   tree, a `gh-cassette.json`, a `sonar-fixture.json`. Not every eval needs
   every fixture type.
3. Include both positive cases (clean scenario, skill should act) and
   negative cases (ambiguous or invalid scenario, skill should ask or
   decline) -- a one-sided eval set trains one-sided behavior.
4. Run it once by hand, read the transcript, and check the grader's verdict
   actually matches what happened before trusting it going forward.
