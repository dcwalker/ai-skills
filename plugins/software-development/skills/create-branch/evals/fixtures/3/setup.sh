#!/usr/bin/env bash
# Reachable origin; the only ambiguity is the missing issue key in the
# prompt, so any "ask" behavior is isolated to that.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
