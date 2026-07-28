#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-8.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

# Looks finished (clean, committed, pushed) but its PR is still open --
# must NOT be treated as merged/deletable.
git checkout -b feature/awaiting-review --quiet
echo "pending review change" >> pending.txt
git add pending.txt
git commit --quiet -m "Add pending review change"
git push -u origin feature/awaiting-review --quiet

git checkout main --quiet
