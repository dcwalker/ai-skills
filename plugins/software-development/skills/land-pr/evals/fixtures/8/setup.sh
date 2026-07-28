#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-8.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/multi-blocker --quiet
sed -i.bak 's/VERSION = "1.0.0"/VERSION = "1.0.0-rc"/' config.py
rm -f config.py.bak
git add config.py
git commit --quiet -m "Mark version as rc on feature branch"
git push -u origin feature/multi-blocker --quiet

# Base branch moves on independently and touches the same line, so the PR
# starts with a real conflict on top of failing checks.
git checkout main --quiet
sed -i.bak 's/VERSION = "1.0.0"/VERSION = "1.2.0"/' config.py
rm -f config.py.bak
git add config.py
git commit --quiet -m "Bump version to 1.2.0 on main"
git push origin main --quiet

git checkout feature/multi-blocker --quiet
