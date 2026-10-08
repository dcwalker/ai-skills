#!/usr/bin/env bash
# Prepare an isolated environment for one MCP-backed eval trial: a scratch
# workspace and a scratch .mcp.json pointing ONLY at the mcp-stub server(s)
# a fixture provides, in place of any real MCP server. Sibling to
# run-eval.sh, but for a fundamentally different executor mechanism -- see
# below.
#
# Usage: run-mcp-eval.sh <skill-evals-dir> <eval-id> <run-dir>
#
#   <skill-evals-dir>  e.g. plugins/life-skills/skills/triage/evals
#                      Must contain evals.json and fixtures/<eval-id>/.
#   <eval-id>          Numeric id matching evals.json and the fixtures/ subdir.
#   <run-dir>          Fresh directory to build the trial in. Created if
#                      missing; must be empty. Delete it when done -- there
#                      is no separate teardown script, it's just rm -rf.
#
# On success, prints the path to <run-dir>/env.sh. Source it, then invoke
# the trial as a REAL claude subprocess -- not an Agent-tool subagent like
# every other skill's evals use. MCP server resolution happens once when a
# `claude` process starts, so the PATH-injection trick run-eval.sh relies on
# (an in-process subagent's Bash calls picking up a sourced env.sh) has no
# equivalent for MCP: the swap has to happen at process-launch time via
# --strict-mcp-config, which only a separate `claude` invocation can do.
#
#   source "$(evals/lib/run-mcp-eval.sh plugins/life-skills/skills/triage/evals 1 /tmp/eval-run)"
#   cd "$WORKSPACE_DIR"
#   claude -p --dangerously-skip-permissions \
#     --strict-mcp-config --mcp-config "$MCP_CONFIG_PATH" \
#     "<the eval's prompt from evals.json>"
#
# After the trial, grade by diffing $MCP_STUB_STATE_OUT (final Trello state)
# against the fixture's expected-state.json, and/or reading $MCP_STUB_LOG
# (one JSON line per tool call) -- not by trusting the subprocess's stdout
# self-report.
#
# Wires whichever stubs the fixture provides state for -- a fixture with
# both trello-mcp-state.json and gmail-mcp-state.json gets both servers in
# one trial (e.g. triage's Step 7c capture-from-email-to-Trello flow). A
# future Jira stub follows the same pattern: its own fixture file check
# below and another entry in the generated mcpServers object.

set -euo pipefail

# Some shells print the resolved directory as a side effect of `cd` itself
# (e.g. when CDPATH is set) -- redirect cd's own stdout everywhere below so
# only the explicit `pwd` is captured, not a doubled/newline-joined value.
unset CDPATH
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"
# shellcheck source=isolation-env.sh
source "$SCRIPT_DIR/isolation-env.sh"

if [[ ! -d "$1" ]]; then
  echo "run-mcp-eval: no such skill evals dir: $1" >&2
  exit 1
fi
SKILL_EVALS_DIR="$(cd "$1" > /dev/null && pwd)"
EVAL_ID="$2"
RUN_DIR="$3"

FIXTURE_DIR="$SKILL_EVALS_DIR/fixtures/$EVAL_ID"
if [[ ! -d "$FIXTURE_DIR" ]]; then
  echo "run-mcp-eval: no fixture directory at $FIXTURE_DIR" >&2
  exit 1
fi

MCP_STUB_DIR="$SCRIPT_DIR/mcp-stub"
MCP_STUB_PYTHON="$MCP_STUB_DIR/.venv/bin/python3"
if [[ ! -x "$MCP_STUB_PYTHON" ]]; then
  echo "run-mcp-eval: mcp-stub venv not found at $MCP_STUB_PYTHON -- see evals/lib/mcp-stub/requirements.txt" >&2
  exit 1
fi

mkdir -p "$RUN_DIR"
RUN_DIR="$(cd "$RUN_DIR" > /dev/null && pwd)"
WORKSPACE_DIR="$RUN_DIR/workspace"

if [[ -d "$FIXTURE_DIR/repo" ]] || [[ -f "$FIXTURE_DIR/setup.sh" ]] || [[ -f "$FIXTURE_DIR/meta.json" ]]; then
  "$SCRIPT_DIR/git-fixture.sh" "$FIXTURE_DIR" "$WORKSPACE_DIR" > /dev/null
else
  mkdir -p "$WORKSPACE_DIR"
fi

MCP_SERVERS_JSON="{}"

# add_stub_server <service> <stub script>: if the fixture has
# <service>-mcp-state.json, add that stub to the generated config with
# per-service state-out/log paths in $RUN_DIR. The stub is seeded from
# $RUN_DIR/<service>-state-seed.json, the fixture with its dates moved to the
# run date by fixture-dates.py (unchanged when the fixture names no
# anchor_date). Grade final state against that seed, not the fixture file.
add_stub_server() {
  local service="$1" stub_script="$2"
  local fixture_state="$FIXTURE_DIR/$service-mcp-state.json"
  [[ -f "$fixture_state" ]] || return 0
  local state_file="$RUN_DIR/$service-state-seed.json"
  python3 "$SCRIPT_DIR/fixture-dates.py" state "$FIXTURE_DIR" "$fixture_state" "$state_file"
  MCP_SERVERS_JSON=$(python3 -c "
import json, sys
servers = json.loads(sys.argv[1])
servers[sys.argv[2]] = {
    'command': sys.argv[3],
    'args': [sys.argv[4]],
    'env': {
        'MCP_STUB_STATE_FILE': sys.argv[5],
        'MCP_STUB_STATE_OUT': sys.argv[6],
        'MCP_STUB_LOG': sys.argv[7],
    },
}
print(json.dumps(servers))
" "$MCP_SERVERS_JSON" "$service" "$MCP_STUB_PYTHON" "$MCP_STUB_DIR/$stub_script" \
    "$state_file" "$RUN_DIR/$service-state-out.json" "$RUN_DIR/$service-calls.log")
}

add_stub_server trello trello_stub.py
add_stub_server gmail gmail_stub.py
add_stub_server atlassian jira_stub.py
add_stub_server slack slack_stub.py
add_stub_server calendar calendar_stub.py

if [[ "$MCP_SERVERS_JSON" == "{}" ]]; then
  echo "run-mcp-eval: fixture $FIXTURE_DIR provides no recognized *-mcp-state.json file" >&2
  exit 1
fi

# The eval's expected output and expectations, with the same date tokens
# resolved, for whoever grades the trial.
if [[ -f "$SKILL_EVALS_DIR/evals.json" ]]; then
  python3 "$SCRIPT_DIR/fixture-dates.py" eval "$SKILL_EVALS_DIR/evals.json" "$EVAL_ID" \
    "$FIXTURE_DIR" "$RUN_DIR/eval.json"
fi

MCP_CONFIG_PATH="$RUN_DIR/mcp-config.json"
python3 -c "
import json, sys
json.dump({'mcpServers': json.loads(sys.argv[1])}, open(sys.argv[2], 'w'), indent=2)
" "$MCP_SERVERS_JSON" "$MCP_CONFIG_PATH"

ENV_FILE="$RUN_DIR/env.sh"
{
  echo "export WORKSPACE_DIR=\"$WORKSPACE_DIR\""
  echo "export MCP_CONFIG_PATH=\"$MCP_CONFIG_PATH\""

  # --strict-mcp-config keeps the trial off the real MCP servers, but it only
  # governs MCP. The `claude` subprocess still inherits the caller's shell and
  # can shell out, and triage/SKILL.md documents two such paths: a curl -X POST
  # to Jira's REST API using ATLASSIAN_USER_* credentials, and gh pr view /
  # gh search prs. Neither goes through MCP. The same isolation preamble
  # run-eval.sh uses covers both -- scrubbing the credentials, and shadowing gh,
  # which authenticates from its own keyring and so ignores GH_TOKEN entirely.
  emit_isolation_env "$SCRIPT_DIR"
  echo "export GH_STUB_LOG=\"$RUN_DIR/gh-calls.log\""
  echo "export GH_STUB_COUNTS_DIR=\"$RUN_DIR\""
  # organize-meeting-notes creates cards through its bundled script rather
  # than MCP; the same hook run-eval.sh wires serves that script canned
  # responses. Without it the script refuses to run under AI_SKILLS_EVAL.
  if [[ -f "$FIXTURE_DIR/trello-fixture.json" ]]; then
    echo "export TRELLO_FIXTURE_FILE=\"$FIXTURE_DIR/trello-fixture.json\""
    echo "export TRELLO_FIXTURE_COUNTS_DIR=\"$RUN_DIR\""
    echo "export TRELLO_FIXTURE_LOG=\"$RUN_DIR/trello-calls.log\""
  fi
  # Per-service grading artifacts (only for services this fixture wired up):
  for SERVICE in trello gmail atlassian slack calendar; do
    if [[ -f "$FIXTURE_DIR/$SERVICE-mcp-state.json" ]]; then
      VAR="$(echo "$SERVICE" | tr '[:lower:]' '[:upper:]')"
      echo "export ${VAR}_STATE_SEED=\"$RUN_DIR/$SERVICE-state-seed.json\""
      echo "export ${VAR}_STATE_OUT=\"$RUN_DIR/$SERVICE-state-out.json\""
      echo "export ${VAR}_CALLS_LOG=\"$RUN_DIR/$SERVICE-calls.log\""
    fi
  done
} > "$ENV_FILE"

echo "$ENV_FILE"
