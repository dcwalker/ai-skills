#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-9.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/auto-deleted --quiet
echo "auto deleted change" >> auto.txt
git add auto.txt
git commit --quiet -m "Add auto-deleted change"
git push -u origin feature/auto-deleted --quiet
git checkout main --quiet
git merge --no-ff feature/auto-deleted --quiet -m "Merge feature/auto-deleted"
git push origin main --quiet

# Host auto-deleted the remote branch on merge; only the local branch remains.
git push origin --delete feature/auto-deleted --quiet

git checkout main --quiet
