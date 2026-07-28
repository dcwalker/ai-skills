#!/usr/bin/env bash
# origin is configured but unreachable -- `git ls-remote` will fail, so the
# skill should create the local branch and skip publishing silently.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

git remote add origin /nonexistent/path/origin.git
