#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-5.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/no-pr-yet --quiet
echo "def draft_only():" >> config.py
echo "    return None" >> config.py
git add config.py
git commit --quiet -m "Work in progress, no PR opened yet"
git push -u origin feature/no-pr-yet --quiet
