#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-10.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b PROJ-123-add-avatar-upload --quiet
echo "avatar upload" >> avatar.txt
git add avatar.txt
git commit --quiet -m "PROJ-123: add avatar upload"
git push -u origin PROJ-123-add-avatar-upload --quiet
git checkout main --quiet
git merge --no-ff PROJ-123-add-avatar-upload --quiet -m "Merge PROJ-123-add-avatar-upload"
git push origin main --quiet

git checkout main --quiet
