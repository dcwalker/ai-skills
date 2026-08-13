#!/usr/bin/env bash
# Build a scratch git repo for a single eval trial from a fixture directory.
#
# Usage: git-fixture.sh <fixture-dir> <workspace-dir>
#
# Fixture directory layout (all parts optional):
#   repo/          Working tree to seed as the initial commit.
#   setup.sh       Run with CWD = the fresh repo, after the initial commit,
#                  to create additional branches/commits/tags. Receives the
#                  workspace dir as $1 for scripts that prefer not to rely on CWD.
#   meta.json      {"checkout": "<branch>"} -- branch to leave checked out
#                  when setup finishes. Defaults to the initial branch.
#
# Each call produces an isolated repo in <workspace-dir> with local-only git
# config (no dependency on, or interference with, the host's global git
# config), so trials never share state.

set -euo pipefail

# Some shells print the resolved directory as a side effect of `cd` itself
# (e.g. when CDPATH is set) -- redirect cd's own stdout everywhere below so
# only the explicit `pwd` is captured, not a doubled/newline-joined value.
unset CDPATH

if [[ ! -d "$1" ]]; then
  echo "git-fixture: fixture dir does not exist: $1" >&2
  exit 1
fi
FIXTURE_DIR="$(cd "$1" > /dev/null && pwd)"
WORKSPACE_DIR_ARG="$2"

if [[ -e "$WORKSPACE_DIR_ARG" ]] && [[ -n "$(ls -A "$WORKSPACE_DIR_ARG" 2>/dev/null)" ]]; then
  echo "git-fixture: workspace dir must not exist or must be empty: $WORKSPACE_DIR_ARG" >&2
  exit 1
fi

# Resolve to an absolute path before any `cd` below -- a relative path here
# would otherwise be silently re-interpreted against the new cwd once we cd
# into it, causing $FIXTURE_DIR/repo etc. to resolve to the wrong place.
mkdir -p "$WORKSPACE_DIR_ARG"
WORKSPACE_DIR="$(cd "$WORKSPACE_DIR_ARG" > /dev/null && pwd)"
cd "$WORKSPACE_DIR"

git init --initial-branch=main --quiet
git config user.name "Eval Fixture"
git config user.email "eval-fixture@localhost"
git config commit.gpgsign false

if [[ -d "$FIXTURE_DIR/repo" ]]; then
  cp -R "$FIXTURE_DIR/repo/." "$WORKSPACE_DIR/"
  git add -A
  git commit --quiet -m "Initial fixture state"
else
  git commit --quiet --allow-empty -m "Initial fixture state (empty repo)"
fi

if [[ -f "$FIXTURE_DIR/setup.sh" ]]; then
  # Pin init.defaultBranch for the setup subprocess. The workspace repo above
  # is created with an explicit --initial-branch=main, but a fixture that
  # builds its own bare origin with a plain `git init --bare` inherits the
  # HOST's default instead. On a machine where init.defaultBranch is unset,
  # that origin comes up with HEAD -> refs/heads/master while the fixture only
  # ever pushes main, so a later `git remote set-head origin --auto` cannot
  # resolve and aborts the whole fixture under `set -e`.
  #
  # The failure is total and early: run-eval.sh dies before writing env.sh or
  # in-trial.sh, so the trial is unrunnable rather than merely odd. It is also
  # invisible on any machine that happens to set init.defaultBranch=main, which
  # is why 25 fixtures across `pr` and `create-branch` carried it unnoticed --
  # every one of the 15 `pr` trials in the first benchmark run hit it and had to
  # work around it by hand.
  #
  # Set here rather than in each fixture so new fixtures inherit the guarantee.
  # A fixture passing --initial-branch explicitly still wins: the command line
  # beats config. The triplet is scoped to this subprocess and never reaches
  # env.sh, which unsets it for the trial itself.
  GIT_CONFIG_COUNT=1 \
  GIT_CONFIG_KEY_0=init.defaultBranch \
  GIT_CONFIG_VALUE_0=main \
    bash "$FIXTURE_DIR/setup.sh" "$WORKSPACE_DIR"
fi

if [[ -f "$FIXTURE_DIR/meta.json" ]]; then
  CHECKOUT_BRANCH=$(python3 -c "
import json, sys
meta = json.load(open('$FIXTURE_DIR/meta.json'))
print(meta.get('checkout', ''))
")
  if [[ -n "$CHECKOUT_BRANCH" ]]; then
    git checkout --quiet "$CHECKOUT_BRANCH"
  fi
fi

echo "$WORKSPACE_DIR"
