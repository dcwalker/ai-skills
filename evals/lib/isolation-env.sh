#!/usr/bin/env bash
#
# isolation-env.sh -- the single definition of what a trial environment must
# NOT be able to reach.
#
# Sourced by run-eval.sh and run-mcp-eval.sh. Both harnesses emit the same
# isolation preamble into their generated env.sh, so a credential added here
# is scrubbed by both. Keeping two copies in sync by hand is how the Atlassian
# credentials were missed after the Trello incident.
#
# Usage:
#   source "$SCRIPT_DIR/isolation-env.sh"
#   emit_isolation_env "$SCRIPT_DIR"   # writes `export`/`unset` lines to stdout

# Every real service credential a bundled script or a skill's documented
# fallback might read. Scrubbing is necessary but never sufficient on its own:
# a CLI with its own stored auth (gh) ignores these entirely, which is why the
# gh stub goes on PATH as well.
EVAL_SCRUBBED_CREDENTIALS=(
  # Trello -- create-trello-task.sh real mode.
  TRELLO_API_KEY
  TRELLO_TOKEN
  TRELLO_LIST_ID
  TRELLO_BOARD_ID
  TRELLO_WORKSPACE_ID
  # Sonar -- list-sonar-issues.py real mode.
  SONAR_TOKEN
  SONAR_HOST_URL
  SONAR_PROJECT_KEY
  # GitHub -- env-var auth only; see the PATH note above for the real defence.
  GH_TOKEN
  GITHUB_TOKEN
  # Atlassian -- triage/SKILL.md documents a curl -X POST to
  # /rest/api/3/issue/{key}/comment using these. That path never goes through
  # MCP, so --strict-mcp-config does not cover it.
  ATLASSIAN_USER_EMAIL
  ATLASSIAN_USER_API_KEY
  ATLASSIAN_API_TOKEN
  ATLASSIAN_SITE_URL
  JIRA_API_TOKEN
  JIRA_BASE_URL
  JIRA_EMAIL
)

# Emit the isolation preamble. $1 is evals/lib, so the gh stub can be placed
# ahead of the real gh on PATH.
emit_isolation_env() {
  local lib_dir="$1"

  # Marks the environment as a trial. Bundled scripts that can reach a real
  # service check this and refuse rather than falling back to real mode, so a
  # missing fixture file fails loudly instead of hitting a live account.
  echo "export AI_SKILLS_EVAL=1"

  local cred
  for cred in "${EVAL_SCRUBBED_CREDENTIALS[@]}"; do
    echo "unset $cred"
  done

  # Point anything that reads a host at an unroutable name, so a script that
  # ignores both the marker and the missing credentials still cannot reach a
  # real service.
  echo "export SONAR_HOST_URL=\"https://sonar.invalid\""
  echo "export SONAR_TOKEN=\"eval-fixture-token\""

  # gh authenticates from its own keyring/hosts.yml after `gh auth login` and
  # does not need GH_TOKEN, so unsetting tokens does not stop it. Shadowing the
  # binary does: the stub refuses without a cassette and never execs real gh.
  echo "export PATH=\"$lib_dir/gh-stub:\$PATH\""
}
