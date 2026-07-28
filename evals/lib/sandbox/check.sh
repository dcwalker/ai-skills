#!/usr/bin/env bash
# Gate for the small set of "golden path" evals that run against a real,
# disposable GitHub sandbox repo instead of the gh-stub.
#
# Usage: check.sh
#   Exit 0  -- sandbox is configured; EVAL_GH_SANDBOX_REPO and
#              EVAL_GH_SANDBOX_TOKEN are set, prints "owner/repo" on stdout.
#   Exit 77 -- sandbox is not configured; the eval should be SKIPPED, not
#              failed. 77 is the conventional "skip" exit code (used by
#              automake/prove-style test runners) so callers can distinguish
#              "not set up yet" from "actually broken."
#
# Setting up the sandbox is a one-time, out-of-band action: create a throwaway
# GitHub repo dedicated to eval runs, and a token scoped to just that repo
# with repo-write access. Do not point this at a real project repo -- these
# evals create and mutate PRs/issues/branches as part of normal operation.

set -euo pipefail

if [[ -z "${EVAL_GH_SANDBOX_REPO:-}" ]] || [[ -z "${EVAL_GH_SANDBOX_TOKEN:-}" ]]; then
  echo "sandbox eval skipped: EVAL_GH_SANDBOX_REPO and/or EVAL_GH_SANDBOX_TOKEN not set" >&2
  exit 77
fi

echo "$EVAL_GH_SANDBOX_REPO"
