#!/usr/bin/env bash
# Baseline: origin remote is a reachable bare repo, main is pushed. The
# skill should be able to create and push a branch cleanly.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
