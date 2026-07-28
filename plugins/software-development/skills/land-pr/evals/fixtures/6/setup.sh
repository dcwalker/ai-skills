#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-6.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/still-drafting --quiet
echo "def draft_feature():" >> config.py
echo "    return \"wip\"" >> config.py
git add config.py
git commit --quiet -m "Draft feature() implementation"
git push -u origin feature/still-drafting --quiet
