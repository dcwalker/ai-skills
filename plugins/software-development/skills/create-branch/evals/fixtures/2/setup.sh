#!/usr/bin/env bash
# Baseline with a reachable origin, for a GitHub-issue-keyed branch. A
# gh-cassette.json supplies the `gh issue comment` response for step 6.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
