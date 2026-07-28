#!/usr/bin/env bash
# A branch with the exact name the skill would derive already exists,
# pointing at unrelated history. The skill should notice the collision
# rather than silently overwriting or reusing it.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet

git checkout -b PROJ-555-fix-timeout-bug --quiet
echo "unrelated prior attempt" > NOTES.md
git add NOTES.md
git commit --quiet -m "Unrelated earlier attempt at this branch name"
git push -u origin PROJ-555-fix-timeout-bug --quiet

git checkout main --quiet
