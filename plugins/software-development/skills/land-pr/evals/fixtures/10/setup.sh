#!/usr/bin/env bash
# PR #510: one failing check in round 1 that reports its own check-run URL,
# green on the refresh. Grades whether the step 4 report cites the PR and the
# check as links rather than as a bare "#510" and a bare check name.
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-10.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/link-report --quiet
echo "def reporting():" >> config.py
echo "    return True" >> config.py
git add config.py
git commit --quiet -m "Add reporting() helper"
git push -u origin feature/link-report --quiet
