#!/usr/bin/env bash
# Prepare an isolated environment for one eval trial: a scratch git repo,
# the gh-stub on PATH, and any fixture env vars the skill's bundled scripts
# look for. Does NOT run the skill itself -- the executor is a Claude
# subagent (per skill-creator's model), not a shell process, so this script's
# job ends at "environment is ready" and prints an env.sh to source.
#
# Usage: run-eval.sh <skill-evals-dir> <eval-id> <run-dir>
#
#   <skill-evals-dir>  e.g. plugins/software-development/skills/commit/evals
#                      Must contain evals.json and fixtures/<eval-id>/.
#   <eval-id>          Numeric id matching evals.json and the fixtures/ subdir.
#   <run-dir>          Fresh directory to build the trial in. Created if
#                      missing; must be empty. Delete it when done -- there
#                      is no separate teardown script, it's just rm -rf.
#
# On success, prints the path to <run-dir>/env.sh. Source it before invoking
# the skill:
#   source "$(evals/lib/run-eval.sh <skill-evals-dir> <eval-id> <run-dir>)"
#   cd "$WORKSPACE_DIR"

set -euo pipefail

# Some shells print the resolved directory as a side effect of `cd` itself
# (e.g. when CDPATH is set) -- redirect cd's own stdout everywhere below so
# only the explicit `pwd` is captured, not a doubled/newline-joined value.
unset CDPATH
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

if [[ ! -d "$1" ]]; then
  echo "run-eval: no such skill evals dir: $1" >&2
  exit 1
fi
# Resolve to absolute paths up front -- git-fixture.sh cd's into the
# workspace, and a relative path passed through would otherwise be silently
# re-interpreted against the new cwd instead of the caller's.
SKILL_EVALS_DIR="$(cd "$1" > /dev/null && pwd)"
EVAL_ID="$2"
RUN_DIR="$3"

FIXTURE_DIR="$SKILL_EVALS_DIR/fixtures/$EVAL_ID"
if [[ ! -d "$FIXTURE_DIR" ]]; then
  echo "run-eval: no fixture directory at $FIXTURE_DIR" >&2
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

SKILL_SCRIPTS_DIR="$(dirname "$SKILL_EVALS_DIR")/scripts"

ENV_FILE="$RUN_DIR/env.sh"
{
  echo "export WORKSPACE_DIR=\"$WORKSPACE_DIR\""
  if [[ -d "$SKILL_SCRIPTS_DIR" ]]; then
    # Real Claude Code sessions put an active skill's bundled scripts/ dir on
    # PATH automatically; a subagent executor trial doesn't inherit that, so
    # reproduce it here rather than relying on the executor to guess a path.
    echo "export PATH=\"$SCRIPT_DIR/gh-stub:$SKILL_SCRIPTS_DIR:\$PATH\""
  else
    echo "export PATH=\"$SCRIPT_DIR/gh-stub:\$PATH\""
  fi
  echo "export GH_STUB_LOG=\"$RUN_DIR/gh-calls.log\""
  echo "export GH_STUB_COUNTS_DIR=\"$RUN_DIR\""

  if [[ -f "$FIXTURE_DIR/gh-cassette.json" ]]; then
    echo "export GH_STUB_CASSETTE=\"$FIXTURE_DIR/gh-cassette.json\""
  fi

  if [[ -f "$FIXTURE_DIR/sonar-fixture.json" ]]; then
    echo "export SONAR_FIXTURE_FILE=\"$FIXTURE_DIR/sonar-fixture.json\""
    echo "export SONAR_FIXTURE_COUNTS_DIR=\"$RUN_DIR\""
    echo "export SONAR_HOST_URL=\"https://sonar.invalid\""
    echo "export SONAR_TOKEN=\"eval-fixture-token\""

    if [[ -f "$FIXTURE_DIR/sonar-project-key" ]]; then
      PROJECT_KEY="$(cat "$FIXTURE_DIR/sonar-project-key")"
      echo "export SONAR_PROJECT_KEY=\"$PROJECT_KEY\""
    fi
  fi

  if [[ -f "$FIXTURE_DIR/trello-fixture.json" ]]; then
    echo "export TRELLO_FIXTURE_FILE=\"$FIXTURE_DIR/trello-fixture.json\""
    echo "export TRELLO_FIXTURE_COUNTS_DIR=\"$RUN_DIR\""
    echo "export TRELLO_FIXTURE_LOG=\"$RUN_DIR/trello-calls.log\""
  fi
} > "$ENV_FILE"

echo "$ENV_FILE"
