#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-3.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/awaiting-approval --quiet
echo "def status():" >> config.py
echo "    return \"ok\"" >> config.py
git add config.py
git commit --quiet -m "Add status() helper"
git push -u origin feature/awaiting-approval --quiet
