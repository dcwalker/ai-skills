#!/usr/bin/env bash
# The checked-out branch has zero commits ahead of origin/HEAD -- there is
# nothing to open a PR for.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 170-planned-cleanup --quiet
# Intentionally no commits on this branch beyond main's tip.
