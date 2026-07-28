#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
PARENT_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)"
BARE_DIR="$PARENT_DIR/origin-3.git"
WT_DIR="$PARENT_DIR/wt-3-stale"
rm -rf "$BARE_DIR" "$WT_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/reviewed-and-merged --quiet
echo "reviewed change" >> reviewed.txt
git add reviewed.txt
git commit --quiet -m "Add reviewed change"
git push -u origin feature/reviewed-and-merged --quiet
git checkout main --quiet
git merge --no-ff feature/reviewed-and-merged --quiet -m "Merge feature/reviewed-and-merged"
git push origin main --quiet

# Delete the branch upstream (simulating the host's auto-delete-on-merge)
# while it's still checked out locally in a worktree.
git push origin --delete feature/reviewed-and-merged --quiet

git worktree add "$WT_DIR" feature/reviewed-and-merged --quiet

git checkout main --quiet
