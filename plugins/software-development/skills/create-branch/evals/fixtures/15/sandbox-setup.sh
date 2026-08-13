#!/usr/bin/env bash
# Sandbox setup for create-branch eval 15 -- the positive counterpart to eval
# 14's "do not fabricate a link."
#
# Run by run-eval.sh with the trial environment already sourced, so
# EVAL_GH_SANDBOX_REPO, GH_TOKEN and GIT_ASKPASS are set and both git and gh
# can reach the disposable repo.
#
# Why this eval needs a real remote rather than a fixture: the skill derives
# the branch URL from `git remote get-url origin`, and it only publishes at all
# when `git ls-remote --exit-code origin HEAD` succeeds. A fabricated
# github.com origin satisfies the first and fails the second -- nothing offline
# satisfies both, which is why eval 14 can only cover the negative half.
set -euo pipefail

WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ISSUE_NUMBER=1
BRANCH_PREFIX="gh-${ISSUE_NUMBER}-"

git remote add origin "https://github.com/${EVAL_GH_SANDBOX_REPO}.git"

# Seed check. The eval prompt names issue #1 by number, so the repo has to have
# it; fail loudly with the fix rather than letting the trial run and grade a
# `gh issue comment` failure as a skill defect.
if ! gh issue view "$ISSUE_NUMBER" --json number > /dev/null 2>&1; then
  echo "create-branch/15: sandbox repo ${EVAL_GH_SANDBOX_REPO} has no issue #${ISSUE_NUMBER}." >&2
  echo "  Seed it once:  gh issue create --repo ${EVAL_GH_SANDBOX_REPO} \\" >&2
  echo "    --title 'Support keyboard navigation in the dropdown menu' --body 'Eval fixture issue.'" >&2
  exit 1
fi

# Clear branches a previous trial pushed. Without this the skill hits a
# name collision it did not cause, and eval 11's collision case -- which is
# where that behavior belongs -- stops being the only place it is graded.
while read -r stale; do
  [[ -n "$stale" ]] && git push --quiet origin --delete "$stale"
done < <(git ls-remote --heads origin "${BRANCH_PREFIX}*" | sed 's|.*refs/heads/||')

# The workspace's main is deliberately not pushed: its history is unrelated to
# whatever the sandbox repo already has, so a push would either be rejected or
# need a force. The skill only needs origin to be reachable and writable, and
# the branch it creates lands as a new ref with its own history.
