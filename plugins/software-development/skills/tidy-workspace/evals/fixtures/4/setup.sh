#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-4.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/done-and-merged --quiet
echo "done change" >> done.txt
git add done.txt
git commit --quiet -m "Add done change"
git push -u origin feature/done-and-merged --quiet
git checkout main --quiet
git merge --no-ff feature/done-and-merged --quiet -m "Merge feature/done-and-merged"
git push origin main --quiet

# Leftover uncommitted scratch file too, so the plan has more than one item.
echo "scratch output" > scratch.out

git checkout main --quiet
