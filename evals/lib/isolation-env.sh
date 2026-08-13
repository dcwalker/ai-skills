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

# Neutralize the host's git configuration for the trial.
#
# A fixture sets its origin remote to a literal URL (e.g.
# https://github.com/acme/widgets.git) and skills derive owner/repo from it by
# pattern-matching `git remote get-url origin`. Any `url.<base>.insteadOf` the
# developer has configured rewrites that value before the skill ever sees it --
# `git remote get-url` returns the rewritten URL, not the configured one. A
# corporate git proxy rewrite turns acme/widgets into the proxy's host and path,
# and the skill derives a repo that does not exist; an SSH-preferring rewrite
# changes the form the skill has to parse. Either way the fixture no longer
# means what it says, and the failure looks like a skill bug.
#
# Rewrites can arrive three ways, so all three are closed: config files
# (GIT_CONFIG_GLOBAL/GIT_CONFIG_SYSTEM) and the GIT_CONFIG_COUNT/KEY/VALUE
# environment triplet, which git treats as command-line-level config and which
# therefore outranks both files. Per-repo config is untouched -- git-fixture.sh
# sets identity there, and the fixture's own remotes must survive.
emit_git_config_isolation() {
  echo "export GIT_CONFIG_GLOBAL=/dev/null"
  echo "export GIT_CONFIG_SYSTEM=/dev/null"

  local i
  for ((i = 0; i < ${GIT_CONFIG_COUNT:-0}; i++)); do
    echo "unset GIT_CONFIG_KEY_$i GIT_CONFIG_VALUE_$i"
  done
  echo "unset GIT_CONFIG_COUNT"

  return 0
}

# Emit the isolation preamble. $1 is evals/lib, so the gh stub can be placed
# ahead of the real gh on PATH. $2 is the mode: "stub" (default) shadows gh;
# "sandbox" is for the handful of evals that run against a real disposable
# GitHub repo, and deliberately leaves the real gh reachable -- run-eval.sh
# gives it the sandbox-scoped token and nothing else. Both modes scrub every
# credential; the mode only decides whether gh is shadowed.
emit_isolation_env() {
  local lib_dir="$1"
  local mode="${2:-stub}"

  # Marks the environment as a trial. Bundled scripts that can reach a real
  # service check this and refuse rather than falling back to real mode, so a
  # missing fixture file fails loudly instead of hitting a live account.
  echo "export AI_SKILLS_EVAL=1"

  emit_git_config_isolation

  # Every credential is scrubbed in every mode, sandbox included. A sandbox
  # trial does need a GitHub token, but it gets exactly one: run-eval.sh emits
  # `export GH_TOKEN="$EVAL_GH_SANDBOX_TOKEN"` *after* this preamble, so the
  # unset below is what guarantees the host's token cannot survive into the
  # trial -- only the sandbox-scoped one is put back.
  #
  # GITHUB_TOKEN is deliberately never re-exported. gh prefers GH_TOKEN and so
  # needs nothing else, and leaving GITHUB_TOKEN populated would hand anything
  # that reads it directly whatever ambient credential the host had. That is
  # not hypothetical: GitHub Actions injects a GITHUB_TOKEN into every job, so
  # a sandbox eval run in CI would otherwise inherit the workflow's own,
  # much broader, token -- exactly the "one throwaway repo, nothing else"
  # boundary this mode exists to draw.
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
  # A sandbox trial is the one case that wants the real binary, so the stub
  # stays off PATH there.
  if [[ "$mode" != "sandbox" ]]; then
    echo "export PATH=\"$lib_dir/gh-stub:\$PATH\""
  fi

  # Explicit: a caller under `set -e` must not inherit the exit status of
  # whatever the last echo happened to be.
  return 0
}
