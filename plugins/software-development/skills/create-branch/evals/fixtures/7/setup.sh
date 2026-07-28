#!/usr/bin/env bash
# Reachable origin; the prompt's title is deliberately long so the branch
# name must be truncated to fit the ~60-72 char guideline.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
