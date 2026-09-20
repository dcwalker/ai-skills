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
│   ├── sonar-scanner-stub/sonar-scanner
│   │                     Fake `sonar-scanner`; reports a successful analysis
│   │                     without contacting anything. See below.
│   ├── git-fixture.sh    Builds a scratch git repo from a fixture spec.
│   ├── run-eval.sh       Per-eval harness: wires fixture + gh-stub + env vars,
│   │                     and writes <run-dir>/in-trial.sh to run commands
│   │                     inside that environment.
│   ├── run-mcp-trials.sh Batch driver for a skill's MCP-backed trials.
│   ├── check-trial-hygiene.sh  Flags trials whose commits carry the
│   │                     orchestrating session's own trailers.
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

### One sourced shell is not enough

The snippet above is only safe while the whole trial stays in a single shell.
Everything that makes a trial isolated lives in `env.sh` -- the credential
`unset`s, the git-config neutralisation, and the `PATH` entry that shadows the
real `gh` with the stub -- and all of it applies only to a shell that sourced
it.

An executor usually drives a trial through a tool that starts a **fresh shell
per command**. It sources `env.sh` once, and every command after that runs
without any of it: the developer's real `TRELLO_*`, `SONAR_*`,
`GH_TOKEN`/`GITHUB_TOKEN` and `ATLASSIAN_*`/`JIRA_*` are back, the host's git
config is back (`url.<base>.insteadOf` included), and `gh` resolves to the real
binary. Nothing announces this. On a machine with no real `gh` the only symptom
is `command not found`, which reads as an ordinary missing tool -- that is how
it went unnoticed through a whole `commit` benchmark, where trials disagreed
about whether `gh` even existed.

So use the wrapper `run-eval.sh` writes next to `env.sh`, for every command:

```bash
/tmp/eval-run/in-trial.sh git status
/tmp/eval-run/in-trial.sh 'git add -A && git commit -m "..."'
```

It sources `env.sh` and `cd`s to the workspace each time. One argument is run as
a shell snippet, so `&&` and pipes work; several are passed through as an argv
vector with no second round of word splitting, so quoted commit messages survive
intact.

### What an executor must be told

Three clauses belong in every executor prompt, because none is enforceable from
the harness side. They apply to Agent-tool subagent executors: the `claude -p`
drivers (`lib/run-mcp-trials.sh` and triage's `run-trials.sh`) pass the eval's
prompt through unchanged, so none of these reach their trials.

1. **Run every command through `in-trial.sh`.** Per the section above.
2. **The executor's own session conventions do not apply inside the trial.**
   The only conventions in scope are the skill's and the fixture's own
   `AGENTS.md`/`CONTRIBUTING.md`. This matters most for commit messages: a
   session instructed to sign commits with `Co-Authored-By: Claude ...` /
   `Claude-Session: ...` will carry that into fixture commits, and in a `commit`
   benchmark the commit message *is* the graded artifact. It happened in 2 of 13
   trials -- intermittent, so it looked like variance rather than a constant
   offset.
3. **Present before acting, as a real session would.** A recap requested for
   the final message does not replace showing the user a plan, draft, or
   question at the point the skill's workflow presents it. Say so explicitly:
   an executor asked to end with "PLAN / REPORT / COMMANDS" tends to act first
   and write the plan only in the recap, which fails every expectation about
   ordering even when the final state is right. In a 2026-09-10
   `tidy-workspace` benchmark, 2 of 3 checked pre-approved trials did this
   without the clause, and 3 of 15 still did with it, so grade ordering
   expectations from the transcript rather than from the executor's final
   message.

`lib/check-trial-hygiene.sh <run-dir>...` is the backstop for the second one.
Run it over the run dirs before writing a baseline; it exits non-zero and names
the offending commits if any trial's messages carry session trailers.

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

## The sonar-scanner stub

`resolve-sonarqube-issues` runs a scan-fix loop, and its *reads* were fixture-
driven long before its *scans* were. Until this stub existed, a trial invoked
whatever real `sonar-scanner` sat on the host's PATH, which broke two things at
once.

It broke isolation, since the one binary in that skill's flow that talks to a
server was the one nothing shadowed. And it broke measurement: the real scanner
fails instantly against the unroutable `SONAR_HOST_URL` the preamble sets, so
the loop aborted after a single iteration. A staged fixture only advances as
reads consume it, so a loop that cannot iterate never reaches the stage where
the project reads clean, and a trial that then (correctly) refused to claim a
clean result off a stale read was marked down for it. Whether an eval converged
depended on how many exploratory calls a trial happened to make, not on whether
it fixed anything.

The stub reports a successful analysis and contacts nothing. It deliberately
does **not** advance the fixture's staged responses: convergence still happens
through reads, exactly as the recorded baselines measured it. What changes is
that the loop can now iterate at all.

`run-eval.sh` sets `SONAR_SCANNER_LOG` alongside the fixture vars, one JSON
line per invocation, so a grader can assert that a scan happened without
constraining the path taken to it.

### Why those expectations read the way they do

Six of this skill's expectations (evals 1, 4, 5, 8, 9 and 10) used to demand
that "a follow-up scan shows zero". None of them was ever graded that way. The
recorded baseline passes them on evidence like *"the fix is real and correct
(verified directly); the static fixture's follow-up check still showed the
pre-fix count due to the harness's padding; the executor was explicit about
this rather than fabricating"* -- which is a different, and better, test: did
the skill actually fix the thing, re-read afterwards, and decline to invent a
clean result it had not seen?

They now say that. The gap mattered: read literally, all six fail on any run
where the staged fixture has not advanced, which is most of them, and the suite
would score around 0.85 while nothing was wrong with the skill. An expectation
that is graded by one standard and written in another cannot be checked by
anyone who was not present for the grading.

Note what this does **not** do. It does not change any run's score, because it
codifies the standard already in use. Convergence is still gated on a read
budget (see above), and eval 7's expectations, which turn on rescan *count* and
on a report saying "0 remain", are untouched -- those are a separate question
about what the loop should do, not about how a scan result is read.

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
- `sonar-scanner-stub` holds the same contract for `sonar-scanner`, and is
  prepended to `PATH` in *every* mode. The sandbox exception exists for evals
  that use a real throwaway GitHub repo; there is no disposable SonarQube
  server, so a real scan from a trial is never wanted.

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

## MCP stub servers (Trello, Gmail, Jira, Slack)

`triage` and `writing` depend on real MCP tools (Trello, Gmail, Jira, and
Slack) rather than a CLI on `PATH`, so they need a different mocking seam
than `gh`/Sonar. `evals/lib/mcp-stub/` holds real,
protocol-compliant MCP stdio servers (built on the official `mcp` Python SDK,
not a hand-rolled JSON-RPC shim) that stand in for the real third-party
server -- `trello_stub.py` implements the subset of Trello tools `triage`
actually calls, `gmail_stub.py` the six Gmail operations its email workflow
(Step 4b) names, and `jira_stub.py` the Atlassian MCP's Jira subset
(including the cloudId-discovery flow via getAccessibleAtlassianResources
and a documented JQL subset that fails loudly on unsupported constructs),
and `slack_stub.py` the search and read operations a corpus-building skill
calls, each backed by an in-memory fake "database" seeded from a fixture
file. Tool names and parameter schemas were confirmed against
live connected MCP servers, not guessed from prose, so a skill's real tool
calls (including name-based list/board resolution and `update_card`'s batch
form) match the stub instead of silently no-oping. Like the real Gmail MCP,
`gmail_stub.py` deliberately has no send operation -- create_draft only
stores a draft, so "sending stayed with the user" holds by construction.
`slack_stub.py` goes the other way and can post, because the real connector
can: a trial where a skill posts unasked has to be a finding about the skill
rather than something the harness made impossible. It is also the one stub
whose *responses* had to be copied rather than shaped, since Slack's tools
return human-readable text in a thin JSON envelope with a different layout
per tool, not structured objects.
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
claude -p --allowedTools "Bash Read Write Edit Glob Grep WebFetch TodoWrite Skill mcp__trello" \
  --strict-mcp-config --mcp-config "$MCP_CONFIG_PATH" \
  -- "<the eval's prompt from evals.json>" < /dev/null
```

Name whichever `mcp__<server>` the fixture wired up; `mcp-config.json` lists
them. An allowlist rather than `--dangerously-skip-permissions` for the reason
in the driver bullets below — that flag is refused outright when the shell is
root. `< /dev/null` stops `-p` waiting three seconds for stdin that is not
coming.

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
carries its own copy of that loop. It matches the shared driver on three
things — the `TRIALS_DIR` override, the skill-plus-`references/` copy, and the
`--allowedTools` allowlist — and on nothing else below: it has no multi-turn
`follow_ups` support and no per-trial `HOME`/`TMPDIR` isolation. Neither gap
fails a trial today — triage's `evals.json` declares no `follow_ups`, none of
its fixtures carry a `home/`, and the skill writes nothing under `$HOME`. The
`HOME` gap is not purely theoretical though: Step 5c reads `~/references/`, so
a triage trial run through its own driver reads whatever that directory holds
on the machine running it, rather than a fixture-controlled one. Folding it
into a caller of this script is the fix, and remains the worthwhile follow-up
its own header calls it.

Both honour a `TRIALS_DIR` environment variable. Output otherwise lands in
`<skill-evals-dir>/.trial-runs/`, which is gitignored but leaves `evals.json`
and `fixtures/` a few directories above each trial's own working directory —
within reach of an executor that goes looking, and that is the answer key.
Point `TRIALS_DIR` outside the repository when that matters:

```bash
TRIALS_DIR=/tmp/writing-trials bash evals/lib/run-mcp-trials.sh \
  plugins/life-skills/skills/writing/evals
```

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
  the working tree rather than the last installed release. What gets copied is
  `SKILL.md` plus `references/` and `scripts/` if present — deliberately not
  the whole directory, which would put `evals.json` and the fixtures inside
  the workspace and hand the trial its own answer key. Both halves matter: a
  skill that splits reference material out of `SKILL.md` has every one of
  those links dangle in the trial copy if only `SKILL.md` is staged, and the
  material behind them goes missing from the measurement without any error.
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
