#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
PARENT_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)"
BARE_DIR="$PARENT_DIR/origin-7.git"
WT_DIR="$PARENT_DIR/wt-7-dirty"
rm -rf "$BARE_DIR" "$WT_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git branch feature/half-done-work main --quiet
git worktree add "$WT_DIR" feature/half-done-work --quiet

# Uncommitted, unpushed changes inside the worktree itself.
echo "half finished idea" >> "$WT_DIR/wip-notes.txt"

git checkout main --quiet
