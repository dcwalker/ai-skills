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
│   ├── gh-stub/gh        Fake `gh` executable, fixture/cassette-driven.
│   ├── git-fixture.sh    Builds a scratch git repo from a fixture spec.
│   ├── run-eval.sh       Per-eval harness: wires fixture + gh-stub + env vars.
│   ├── run-mcp-trials.sh Batch driver for a skill's MCP-backed trials.
│   ├── sandbox/check.sh  Gate for the small set of live sandbox-repo cases.
│   └── sandbox/askpass.sh  Supplies the sandbox token to git without putting
│                         it in the remote URL.
└── README.md             This file.

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
        ├── sonar-project-key Optional: plain-text project key, exported as
        │                      SONAR_PROJECT_KEY when sonar-fixture.json is
        │                      present -- lets a fixture skip shipping a
        │                      sonar-project.properties file in repo/.
        ├── trello-fixture.json Optional: canned create-trello-task.sh
        │                      responses (organize-meeting-notes).
        ├── home/              Optional: seeds the trial's private HOME,
        │                      for skills that keep state across sessions.
        └── sandbox-setup.sh   Optional, `"sandbox": true` evals only: runs
                               with the trial environment sourced, to point
                               origin at the sandbox repo and clear what the
                               previous trial left behind.
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

## Two optional keys in `evals.json`

Both sit at the top level, alongside `skill_name` and `evals`:

```json
{
  "skill_name": "land-pr",
  "repo": "example/widget-service",
  "delegates_to": ["resolve-pr-comments", "fix-pr-checks"],
  "evals": [ ... ]
}
```

`delegates_to` names the sibling skills this one invokes, and puts each of
their `scripts/` dirs on `PATH` alongside the skill's own. A real session does
this implicitly: invoking a sub-skill activates it, bundled scripts included.
A trial does not, so an orchestrating skill loses the very tools it delegates
to -- `land-pr` has no `scripts/` of its own and spent ten trials without
`list-pr-comments.sh` or `list-pr-checks.sh`, quietly measuring a raw-`gh`
fallback instead of the skill. Names are declared rather than inferred from
SKILL.md prose, and an unresolvable one is a hard error: a typo that silently
adds nothing would reproduce the bug this exists to fix.

`repo` is the `owner/repo` slug the cassette's responses are written against,
exported as `GH_REPO` and `GITHUB_REPOSITORY` for stub trials. A fixture's
origin is a local bare repo, so anything deriving owner/repo from the remote
gets a filesystem path and builds requests like
`gh api repos//tmp/run/origin-4.git/pulls/510`. Sandbox evals already set
`GH_REPO` for the same reason; this is the stub-side equivalent.

## The `gh` stub

Set `GH_STUB_CASSETTE` (done automatically by `run-eval.sh` when
`fixtures/<eval-id>/gh-cassette.json` exists) and prepend `evals/lib/gh-stub`
to `PATH`. Every `gh <args>` call is matched against the cassette's `calls`
list by substring or regex against the joined argv -- **not** by strict call
order, so a skill that reaches the same outcome through a different sequence
of `gh` invocations still passes. An unmatched call fails loudly with the
attempted argv, so a fixture gap is obvious immediately rather than silently
returning empty data that makes a grader guess wrong.

A cassette's `default` is the one way to blunt that, and it is worth
understanding before reaching for it. A permissive default -- `{"exit_code":
0, "stdout": "[]"}`, say -- keeps a trial moving past calls nobody fixtured,
but the response it hands back is indistinguishable from a real "nothing
here": a skill can skip a step it should have taken, and grade as correct for
it. The `land-pr` cassettes did exactly this, and three separate trials
reported they could not tell an empty review-comment list from an unfixtured
call. So falling back to `default` **always** writes the attempted argv to
stderr, whatever the default's own `exit_code` and `stderr` say. Prefer a
default that fails (the repo's convention is `{"exit_code": 1, "stderr":
"gh-stub: no fixture match for this call"}`) and fixture the calls your flow
legitimately makes -- including the ones whose honest answer is empty.

Every invocation is also appended to `GH_STUB_LOG` (one JSON line per call,
set automatically by `run-eval.sh`), so a grader can assert on what was or
wasn't called -- e.g. "no `pr merge` call happened," "`pr create` was called
with `--draft`" -- without constraining the exact path taken to get there.

Because responses are canned, a read issued after a write returns the
pre-write fixture state: resolve a thread, and the next listing still shows it
unresolved. That is inherent to replaying a cassette, but it looks exactly like
a write that silently failed. In a 13-trial `resolve-pr-comments` benchmark
every executor spent turns re-reading, grepping the call log, and reasoning it
out before concluding its writes had landed — all thirteen reached the right
answer, and all thirteen paid for it. The stub now prints a one-line note to
stderr the first time a read follows a write, at most once per trial, so the
trial spends its turns on the task rather than on the harness. Writes are
recognized as `-X POST|PATCH|PUT|DELETE` or a GraphQL `mutation`; the note
never touches stdout, which callers parse.

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

## The Trello fixture hook

`organize-meeting-notes`'s bundled `create-trello-task.sh` reads
`TRELLO_FIXTURE_FILE` (an opt-in env var; unset in normal use) and serves a
canned response instead of calling the real Trello API. `run-eval.sh` sets it
automatically when `fixtures/<eval-id>/trello-fixture.json` exists, along
with `TRELLO_FIXTURE_COUNTS_DIR` (each script call is a fresh process, so a
list-valued fixture entry's call-order index has to persist across
invocations via a counts file, the same reason `SONAR_FIXTURE_COUNTS_DIR`
exists) and `TRELLO_FIXTURE_LOG` (one JSON line per call -- `{"text", "desc",
"url"}` or `{"text", "desc", "error"}` -- for graders, mirroring `GH_STUB_LOG`).
See the script's own header comment for the exact fixture JSON format.

## Trials must not be able to reach a real service

Every trial environment is a fail-closed one. This is the invariant to
preserve when adding a stub, a fixture hook, or a bundled script:

- Both harnesses emit the same preamble via `emit_isolation_env` in
  [`isolation-env.sh`](lib/isolation-env.sh), which is the one place the
  credential list lives. Add a service there, not in a harness.
- That preamble exports `AI_SKILLS_EVAL=1`, `unset`s every real service
  credential inherited from the developer's shell (`TRELLO_*`, `SONAR_*`,
  `GH_TOKEN`/`GITHUB_TOKEN`, `ATLASSIAN_*`/`JIRA_*`), and prepends `gh-stub`
  to `PATH`.
- A bundled script that can reach a real service checks `AI_SKILLS_EVAL` and
  **refuses** when its fixture is absent. It must never treat a missing
  fixture as "use the real API." Both `create-trello-task.sh` and
  `list-sonar-issues.py` do this.
- `gh-stub` is the reference: it refuses when `GH_STUB_CASSETTE` is unset and
  never execs the real `gh`.

The same preamble also neutralizes the host's git configuration
(`GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` and the `GIT_CONFIG_COUNT`/`KEY`/
`VALUE` triplet). That is a correctness guard rather than an isolation one: a
fixture sets `origin` to a literal URL and skills derive owner/repo from
`git remote get-url origin`, but `url.<base>.insteadOf` rewrites that value
before the skill sees it. With a proxy rewrite configured,
`https://github.com/acme/widgets.git` comes back as
`http://proxy.internal/git/acme/widgets.git`, every bundled script's
`sed`-based repo detection derives a repo that does not exist, and the
resulting mess grades as a skill defect. Per-repo config is left alone --
`git-fixture.sh` sets identity there and the fixture's own remotes must
survive.

**Scrubbing credentials is necessary but not sufficient.** A CLI with its own
stored auth ignores the environment entirely — `gh` authenticates from its
keyring after `gh auth login` and does not need `GH_TOKEN` — so the stub has
to shadow the binary on `PATH`. And `--strict-mcp-config` only governs MCP: a
skill that documents a `curl` to a REST API (as `triage` does for Jira)
bypasses it completely. Assume every trial can shell out.

A missing fixture file is an authoring oversight, and an oversight must fail
loudly rather than quietly reach a live account. Before this was enforced,
`create-trello-task.sh` selected its mode by the mere absence of
`TRELLO_FIXTURE_FILE`; three evals had no `trello-fixture.json`, the
developer's real Trello credentials were exported by their shell profile, and
a trial created three real cards on a real personal board.

## MCP stub servers (Trello, Gmail, Jira)

`triage` depends on real MCP tools (Trello, Gmail, and Jira) rather than a
CLI on `PATH`, so it needs a different mocking seam than `gh`/Sonar. `evals/lib/mcp-stub/` holds real,
protocol-compliant MCP stdio servers (built on the official `mcp` Python SDK,
not a hand-rolled JSON-RPC shim) that stand in for the real third-party
server -- `trello_stub.py` implements the subset of Trello tools `triage`
actually calls, `gmail_stub.py` the six Gmail operations its email workflow
(Step 4b) names, and `jira_stub.py` the Atlassian MCP's Jira subset
(including the cloudId-discovery flow via getAccessibleAtlassianResources
and a documented JQL subset that fails loudly on unsupported constructs),
each backed by an in-memory fake "database" seeded from a fixture file. Tool names and parameter schemas were confirmed against
live connected MCP servers, not guessed from prose, so a skill's real tool
calls (including name-based list/board resolution and `update_card`'s batch
form) match the stub instead of silently no-oping. Like the real Gmail MCP,
`gmail_stub.py` deliberately has no send operation -- create_draft only
stores a draft, so "sending stayed with the user" holds by construction.
Its query subset also covers `in:sent`, `to:`, and `me` resolution (against
an optional top-level `"me"` address in the fixture), which is what a corpus
search for "mail I wrote to this person" needs; a fixture that declares no
`"me"` makes `from:me`/`to:me` match nothing rather than everything.

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

`run-mcp-eval.sh` wires every `<service>-mcp-state.json` a fixture provides
(`trello-mcp-state.json`, `gmail-mcp-state.json`, `atlassian-mcp-state.json`)
into a scratch
`mcp-config.json` naming those stubs as the *only* MCP servers, so no real
third-party server is reachable during a trial. A fixture that provides
both files gets both stubs in one trial -- how triage's Step 4c
capture-from-email-to-Trello eval runs a genuine cross-service scenario.
After the trial, grade per service by diffing `$RUN_DIR/<service>-state-out.json`
(final state, exported as e.g. `$TRELLO_STATE_OUT`/`$GMAIL_STATE_OUT` in
`env.sh`) against an expected snapshot, and/or reading
`$RUN_DIR/<service>-calls.log` (one JSON line per tool call, e.g.
`$GMAIL_CALLS_LOG`) -- the same "grade final state, not exact steps"
philosophy as every other eval in this repo, not by trusting the
subprocess's stdout self-report.

`evals/lib/run-mcp-trials.sh <skill-evals-dir> [id ...]` is the batch driver
for any skill's MCP-backed trials: it runs each eval's `claude -p` subprocess
with `--output-format json` and extracts real wall-clock duration and token
usage into a per-trial `metrics.json` alongside `transcript.txt`.
`plugins/life-skills/skills/triage/evals/run-trials.sh` predates it and still
carries its own copy of that loop.

Multi-turn trials: an eval may carry a `follow_ups` array of later user
messages alongside its `prompt`. The driver runs the first turn, reads the
session id off its result event, and resumes that same session for each
follow-up, so a revision eval ("draft it", "shorter", "now add this") is a
real conversation rather than one prompt describing three. Every turn's
events land in the same `events.jsonl`, and `transcript.txt` separates them
with `===== turn N =====` markers so a grader can see what each revision
actually changed.

Four things the shared driver does that a hand-run trial must do for itself:

- It copies the skill under test into the trial workspace as a project skill
  (`.claude/skills/<name>/`). A trial subprocess otherwise sees only the
  skills the machine happens to have installed, so on a machine without the
  plugin installed a whole benchmark can measure the skill's *absence* and
  report it as the skill's behavior. Copying also means a benchmark grades
  the working tree rather than the last installed release.
- It passes an explicit `--allowedTools` allowlist instead of
  `--dangerously-skip-permissions`, which refuses to run as root and so rules
  out containers and CI. Each stub server is allowed wholesale, write tools
  included, so "the skill wrote nothing" stays a finding about the skill
  rather than an artifact of the harness blocking the call.
- It gives each trial a private `HOME` and `TMPDIR` under the run directory,
  so a skill that keeps state for the user cannot read what an earlier trial
  left behind. That is both a contamination guard and a privacy one: two
  trials represent two different people. `.claude`, `.claude.json`, and
  `.config` are symlinked back into the trial home so `claude` still
  authenticates, and whatever the skill wrote stays under `$RUN_DIR/home`
  for the grader to read.
- It seeds that home from the fixture's optional `home/` directory, which is
  how a trial starts with state already in place. A fixture can hand the
  trial its own prior cache, or somebody else's, and grade what the skill
  does with each.

## Live sandbox cases

A handful of "golden path" evals per GitHub-touching skill are marked
`"sandbox": true` in `evals.json` and run against a real disposable GitHub
repo instead of the stub, to catch stub/reality drift. They need
`EVAL_GH_SANDBOX_REPO` (`owner/repo`) and `EVAL_GH_SANDBOX_TOKEN` set to a
token scoped to that repo only -- **never point this at a real project
repo**, these evals create and mutate PRs/issues/branches as part of normal
operation. `run-eval.sh` handles the gate itself: for a `"sandbox": true` eval
it calls `lib/sandbox/check.sh` and, when the sandbox isn't configured, exits
`77` (skip, not fail) before building a workspace. Callers must treat `77` as
"not run" rather than as a failure, so the rest of the suite runs fine on a
machine that has no sandbox.

When the sandbox *is* configured, the trial environment differs from every
other eval's in exactly three ways:

- The `gh` stub stays off `PATH`, so the real `gh` runs, holding
  `EVAL_GH_SANDBOX_TOKEN` as `GH_TOKEN` and pinned to the sandbox by
  `GH_REPO`. Every non-GitHub credential is still scrubbed -- "may reach one
  throwaway repo" is not "may reach Trello, Sonar, and Jira."
- git authenticates through `GIT_ASKPASS=lib/sandbox/askpass.sh` instead of a
  token embedded in the remote URL. That is deliberate: skills derive URLs
  from `git remote get-url origin` and then *publish* them to issues and PR
  comments, so a token in the remote would be republished. A clean remote
  makes the worst case a broken link.
- The token is passed by reference, never written into `env.sh` -- so the
  shell that sources `env.sh` must still have `EVAL_GH_SANDBOX_TOKEN`
  exported. `env.sh` says so loudly if it doesn't.

The fixture's optional `sandbox-setup.sh` runs last, with that environment
sourced. It owns pointing `origin` at the sandbox repo and clearing what the
previous trial left behind -- these evals mutate a real repo, so each one has
to start from a known state instead of inheriting the last run's branches.
`create-branch`'s eval 15 is the worked example, and it also shows the one
thing a sandbox eval can need that a fixture can't provide: a seeded issue.
It checks for it and prints the `gh issue create` to run rather than failing
obscurely.

Reach for a sandbox eval when the behavior genuinely cannot be reproduced
offline, not merely because it touches GitHub. `create-branch` 15 is the
case: the skill only publishes when `git ls-remote --exit-code origin HEAD`
succeeds, and derives its link from `git remote get-url origin`. A fabricated
`github.com` origin satisfies the second and fails the first, and no offline
remote satisfies both -- which is why eval 14 can cover only the negative
half ("don't invent a link when none can be derived").

## Adding a new eval

1. Add an entry to the skill's `evals.json` (id, prompt, expected_output,
   expectations).
2. Create `fixtures/<eval-id>/` with whatever the scenario needs: a `repo/`
   tree, a `gh-cassette.json`, a `sonar-fixture.json`, a `trello-fixture.json`,
   or (for `triage`) a `trello-mcp-state.json`. Not every eval needs every
   fixture type.
3. Include both positive cases (clean scenario, skill should act) and
   negative cases (ambiguous or invalid scenario, skill should ask or
   decline) -- a one-sided eval set trains one-sided behavior.
4. Run it once by hand, read the transcript, and check the grader's verdict
   actually matches what happened before trusting it going forward.
