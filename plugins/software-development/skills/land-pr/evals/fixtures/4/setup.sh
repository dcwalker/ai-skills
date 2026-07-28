#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-4.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/always-red --quiet
echo "def broken():" >> config.py
echo "    return 1 / 0" >> config.py
git add config.py
git commit --quiet -m "Add broken() helper"
git push -u origin feature/always-red --quiet
