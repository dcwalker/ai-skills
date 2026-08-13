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

# The number is sandbox-specific and must match the eval prompt, which names
# it. It is not necessarily 1: GitHub numbers issues and pull requests from the
# same sequence, so any PR opened in the sandbox before the fixture issue --
# a plumbing smoke test, say -- takes that number first. Point this and the
# prompt in evals.json at whatever number the fixture issue actually got.
ISSUE_NUMBER=2
ISSUE_TITLE="Support keyboard navigation in the dropdown menu"
BRANCH_PREFIX="gh-${ISSUE_NUMBER}-"

git remote add origin "https://github.com/${EVAL_GH_SANDBOX_REPO}.git"

# Seed check, on the title rather than mere existence. Checking only that the
# number resolves would let a sandbox whose numbering differs pass here and
# then have the trial comment on some unrelated issue, which grades as a skill
# defect. Fail loudly with the fix instead.
FOUND_TITLE="$(gh issue view "$ISSUE_NUMBER" --json title --jq .title 2>/dev/null || true)"
if [[ "$FOUND_TITLE" != "$ISSUE_TITLE" ]]; then
  echo "create-branch/15: ${EVAL_GH_SANDBOX_REPO} issue #${ISSUE_NUMBER} is not the fixture issue." >&2
  if [[ -z "$FOUND_TITLE" ]]; then
    echo "  No issue #${ISSUE_NUMBER}. Seed it once:" >&2
    echo "    gh issue create --repo ${EVAL_GH_SANDBOX_REPO} --title '${ISSUE_TITLE}' --body 'Eval fixture issue.'" >&2
    echo "  If the new issue is not #${ISSUE_NUMBER}, update ISSUE_NUMBER here and the prompt in evals.json to match." >&2
  else
    echo "  Expected: ${ISSUE_TITLE}" >&2
    echo "  Found:    ${FOUND_TITLE}" >&2
  fi
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
