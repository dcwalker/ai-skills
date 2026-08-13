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
#
# Exit 77 means SKIP, not fail: the eval is marked `"sandbox": true` in
# evals.json and the disposable GitHub repo it needs is not configured on this
# machine. Callers must treat 77 as "not run" rather than as a failure -- see
# lib/sandbox/check.sh.

set -euo pipefail

# Some shells print the resolved directory as a side effect of `cd` itself
# (e.g. when CDPATH is set) -- redirect cd's own stdout everywhere below so
# only the explicit `pwd` is captured, not a doubled/newline-joined value.
unset CDPATH
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"
# shellcheck source=isolation-env.sh
source "$SCRIPT_DIR/isolation-env.sh"

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

# A "sandbox": true eval runs against a real disposable GitHub repo instead of
# the gh stub, to catch stub/reality drift. Resolve that before building
# anything: when the sandbox is not configured the trial is skipped outright,
# and there is no point creating a workspace for it.
SANDBOX_EVAL=$(python3 -c "
import json, sys
evals = json.load(open('$SKILL_EVALS_DIR/evals.json'))['evals']
match = [e for e in evals if str(e['id']) == '$EVAL_ID']
print('1' if match and match[0].get('sandbox') else '0')
")

SANDBOX_REPO=""
if [[ "$SANDBOX_EVAL" == "1" ]]; then
  set +e
  SANDBOX_REPO="$("$SCRIPT_DIR/sandbox/check.sh")"
  CHECK_STATUS=$?
  set -e
  if [[ $CHECK_STATUS -ne 0 ]]; then
    # 77 (skip) passes straight through; anything else is a real failure.
    exit $CHECK_STATUS
  fi
fi

mkdir -p "$RUN_DIR"
RUN_DIR="$(cd "$RUN_DIR" > /dev/null && pwd)"
WORKSPACE_DIR="$RUN_DIR/workspace"

if [[ -d "$FIXTURE_DIR/repo" ]] || [[ -f "$FIXTURE_DIR/setup.sh" ]] || [[ -f "$FIXTURE_DIR/meta.json" ]]; then
  "$SCRIPT_DIR/git-fixture.sh" "$FIXTURE_DIR" "$WORKSPACE_DIR" > /dev/null
else
  mkdir -p "$WORKSPACE_DIR"
fi

SKILL_DIR="$(dirname "$SKILL_EVALS_DIR")"
SKILLS_ROOT="$(dirname "$SKILL_DIR")"
SKILL_SCRIPTS_DIR="$SKILL_DIR/scripts"

# An orchestrating skill's own scripts/ dir is not enough. When it invokes a
# sub-skill, a real session activates that sub-skill and puts ITS scripts/ dir
# on PATH too -- so `land-pr`, which has no scripts of its own and exists to
# delegate, needs `list-pr-comments.sh` and `list-pr-checks.sh` from
# `resolve-pr-comments` and `fix-pr-checks`. Without them the sub-steps quietly
# degrade to raw `gh` and the trial measures the fallback rather than the
# skill. Declare the delegates in evals.json:
#
#   { "delegates_to": ["resolve-pr-comments", "fix-pr-checks"], "evals": [...] }
#
# Declared rather than inferred: parsing SKILL.md prose for skill names would
# guess, and a typo that silently adds nothing reproduces the very bug this
# fixes -- so an unresolvable name is a hard error here.
DELEGATE_SKILLS=$(python3 -c "
import json
data = json.load(open('$SKILL_EVALS_DIR/evals.json'))
print('\n'.join(data.get('delegates_to', [])))
")

FIXTURE_REPO=$(python3 -c "
import json
data = json.load(open('$SKILL_EVALS_DIR/evals.json'))
print(data.get('repo', ''))
")

SCRIPTS_PATH=""
add_scripts_dir() {
  local dir="$1"
  [[ -d "$dir" ]] || return 0
  if [[ -z "$SCRIPTS_PATH" ]]; then SCRIPTS_PATH="$dir"; else SCRIPTS_PATH="$SCRIPTS_PATH:$dir"; fi
}

add_scripts_dir "$SKILL_SCRIPTS_DIR"
while read -r delegate; do
  [[ -n "$delegate" ]] || continue
  if [[ ! -d "$SKILLS_ROOT/$delegate" ]]; then
    echo "run-eval: evals.json declares delegates_to \"$delegate\", but there is no skill at $SKILLS_ROOT/$delegate" >&2
    exit 1
  fi
  add_scripts_dir "$SKILLS_ROOT/$delegate/scripts"
done <<< "$DELEGATE_SKILLS"

ENV_FILE="$RUN_DIR/env.sh"
{
  echo "export WORKSPACE_DIR=\"$WORKSPACE_DIR\""
  if [[ -n "$SCRIPTS_PATH" ]]; then
    # Real Claude Code sessions put an active skill's bundled scripts/ dir on
    # PATH automatically; a subagent executor trial doesn't inherit that, so
    # reproduce it here rather than relying on the executor to guess a path.
    # emit_isolation_env below prepends the gh stub, so it still wins over any
    # real gh regardless of what this adds.
    echo "export PATH=\"$SCRIPTS_PATH:\$PATH\""
  fi
  echo "export GH_STUB_LOG=\"$RUN_DIR/gh-calls.log\""
  echo "export GH_STUB_COUNTS_DIR=\"$RUN_DIR\""

  # Scrub every real service credential inherited from the caller's shell, and
  # shadow gh. Trials run in the developer's own environment, where these are
  # usually exported by a profile. Without this, a fixture file that was simply
  # never authored leaves a bundled script holding live credentials -- which is
  # how three real Trello cards were created on a personal board during an
  # organize-meeting-notes run. The list lives in isolation-env.sh so this
  # harness and run-mcp-eval.sh cannot drift apart.
  if [[ "$SANDBOX_EVAL" == "1" ]]; then
    emit_isolation_env "$SCRIPT_DIR" sandbox

    # The token is passed by reference, never written into env.sh: env.sh is a
    # plain file in a scratch directory that tends to outlive the trial. The
    # cost is that the shell sourcing it must still have the token exported,
    # so say so rather than letting gh fail as "unauthenticated" later.
    echo ": \"\${EVAL_GH_SANDBOX_TOKEN:?sandbox trial: export EVAL_GH_SANDBOX_TOKEN in the shell that sources env.sh}\""

    # The real gh, holding a token scoped to the disposable repo and nothing
    # else. GH_REPO removes gh's dependence on the origin remote's shape, which
    # a fixture is free to rewrite.
    echo "export EVAL_GH_SANDBOX_REPO=\"$SANDBOX_REPO\""
    echo "export EVAL_GH_SANDBOX_TOKEN=\"\$EVAL_GH_SANDBOX_TOKEN\""
    echo "export GH_TOKEN=\"\$EVAL_GH_SANDBOX_TOKEN\""
    echo "export GH_REPO=\"$SANDBOX_REPO\""

    # git auth for the same repo, via askpass rather than a token embedded in
    # the remote URL -- see the header of sandbox/askpass.sh for why that
    # distinction matters to a skill that publishes the URL it derives.
    echo "export GIT_ASKPASS=\"$SCRIPT_DIR/sandbox/askpass.sh\""
    echo "export GIT_TERMINAL_PROMPT=0"
  else
    emit_isolation_env "$SCRIPT_DIR"
  fi

  if [[ -f "$FIXTURE_DIR/gh-cassette.json" ]]; then
    echo "export GH_STUB_CASSETTE=\"$FIXTURE_DIR/gh-cassette.json\""

    # Same reasoning as the sandbox branch's GH_REPO above, for stub trials: a
    # fixture's origin is a local bare repo, so anything deriving owner/repo
    # from the remote gets a filesystem path. Declare the slug the cassette's
    # responses are written against, in evals.json:
    #
    #   { "repo": "example/widget-service", "evals": [...] }
    if [[ -n "$FIXTURE_REPO" ]]; then
      echo "export GH_REPO=\"$FIXTURE_REPO\""
      echo "export GITHUB_REPOSITORY=\"$FIXTURE_REPO\""
    fi
  fi

  if [[ -f "$FIXTURE_DIR/sonar-fixture.json" ]]; then
    echo "export SONAR_FIXTURE_FILE=\"$FIXTURE_DIR/sonar-fixture.json\""
    echo "export SONAR_FIXTURE_COUNTS_DIR=\"$RUN_DIR\""

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

# A sandbox fixture's setup runs last, with the trial environment already
# sourced, because it needs what env.sh provides: the resolved repo, the token,
# and git/gh auth. It is the place to point origin at the sandbox repo and to
# clear leftovers from a previous run -- these evals mutate a real (disposable)
# repo, so each trial has to start from a known state rather than inheriting
# branches the last one created.
if [[ "$SANDBOX_EVAL" == "1" ]] && [[ -f "$FIXTURE_DIR/sandbox-setup.sh" ]]; then
  (
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    bash "$FIXTURE_DIR/sandbox-setup.sh" "$WORKSPACE_DIR"
  ) >&2
fi

echo "$ENV_FILE"
