#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-9.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/ready-to-land --quiet
echo "def ready():" >> config.py
echo "    return True" >> config.py
git add config.py
git commit --quiet -m "Add ready() helper"
git push -u origin feature/ready-to-land --quiet
