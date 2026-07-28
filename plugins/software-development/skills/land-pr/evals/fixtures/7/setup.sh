#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-7.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/flaky-then-fixed --quiet
echo "def flaky():" >> config.py
echo "    return True" >> config.py
git add config.py
git commit --quiet -m "Add flaky() helper"
git push -u origin feature/flaky-then-fixed --quiet
