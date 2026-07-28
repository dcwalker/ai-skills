#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-2.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/in-progress --quiet
echo "def farewell(name):" >> app.py
echo "    return f\"Bye, {name}!\"" >> app.py
git add app.py
git commit --quiet -m "Add farewell() stub"
# Deliberately do NOT push this branch -- it's unpushed WIP.

# Now leave uncommitted state on top of the committed WIP:
echo "    # TODO: handle empty name" >> app.py
cat > debug.log <<'LOG'
2026-07-27 12:00:00 DEBUG entered farewell()
2026-07-27 12:00:01 DEBUG name=""
LOG
echo "print(greet('scratch'))" > scratch_check.py
