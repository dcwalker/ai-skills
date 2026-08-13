#!/usr/bin/env bash
# GIT_ASKPASS helper for sandbox evals.
#
# git invokes this with the prompt as $1 ("Username for 'https://github.com': "
# or "Password for '...': ") and uses whatever it prints as the answer.
#
# The point of routing the token through askpass rather than embedding it in
# the remote URL: skills derive owner/repo by reading `git remote get-url
# origin`, and several of them then post that derived URL to a GitHub issue or
# a PR comment. A token in the remote URL would be copied into the derived URL
# and published. Keeping the remote clean means the worst case is a broken
# link, not a leaked credential.
#
# Reads EVAL_GH_SANDBOX_TOKEN from the environment; run-eval.sh exports it.

set -euo pipefail

case "${1:-}" in
  Username*) echo "x-access-token" ;;
  Password*) echo "${EVAL_GH_SANDBOX_TOKEN:-}" ;;
  *)
    echo "sandbox askpass: unexpected prompt: ${1:-<none>}" >&2
    exit 1
    ;;
esac
