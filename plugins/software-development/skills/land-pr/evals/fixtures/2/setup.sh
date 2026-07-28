#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-2.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/bump-version --quiet
sed -i.bak 's/VERSION = "1.0.0"/VERSION = "1.0.0-beta"/' config.py
rm -f config.py.bak
git add config.py
git commit --quiet -m "Mark version as beta on feature branch"
git push -u origin feature/bump-version --quiet

# Base branch moves on independently and touches the same line.
git checkout main --quiet
sed -i.bak 's/VERSION = "1.0.0"/VERSION = "1.1.0"/' config.py
rm -f config.py.bak
git add config.py
git commit --quiet -m "Bump version to 1.1.0 on main"
git push origin main --quiet

git checkout feature/bump-version --quiet
