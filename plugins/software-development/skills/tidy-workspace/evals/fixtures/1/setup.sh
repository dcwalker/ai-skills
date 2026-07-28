#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-1.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

# Ancestry-merged branch: a real, non-fast-forward merge into main.
git checkout -b feature/ancestry-merged --quiet
echo "ancestry change" >> notes.txt
git add notes.txt
git commit --quiet -m "Add ancestry note"
git push -u origin feature/ancestry-merged --quiet
git checkout main --quiet
git merge --no-ff feature/ancestry-merged --quiet -m "Merge feature/ancestry-merged"
git push origin main --quiet

# Squash-merged branch: main gets an equivalent but distinct commit, so the
# branch's own commit is never an ancestor of main (ancestry check misses it).
git checkout -b feature/squash-merged --quiet
echo "squash change" >> squash.txt
git add squash.txt
git commit --quiet -m "Add squash change (on branch)"
git push -u origin feature/squash-merged --quiet
git checkout main --quiet
echo "squash change" >> squash.txt
git add squash.txt
git commit --quiet -m "Add squash change (squash-merged via PR #42)"
git push origin main --quiet

git checkout main --quiet
