#!/usr/bin/env bash
# A release/2.4 branch exists with an extra commit beyond main. The user
# will ask for the new branch to be based on release/2.4, not main.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet

git checkout -b release/2.4 --quiet
echo "2.4.0" > VERSION
git add VERSION
git commit --quiet -m "Cut release 2.4"
git push -u origin release/2.4 --quiet

git checkout main --quiet
