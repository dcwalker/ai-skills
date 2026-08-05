#!/usr/bin/env bash
# Reachable origin, but it is a self-hosted git remote -- not a github.com
# URL -- while the work item is a GitHub issue. Step 6 therefore has no
# GitHub repo to derive a branch URL from, so the comment it posts must not
# carry an invented https://github.com/.../tree/<branch> link.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --initial-branch=main --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
