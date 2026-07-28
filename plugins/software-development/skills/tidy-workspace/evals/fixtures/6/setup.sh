#!/usr/bin/env bash
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-6.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

# "develop" is a long-lived, protected integration branch that happens to be
# fully ancestry-merged into main right now -- it must still never appear in
# a deletion list.
git checkout -b develop --quiet
echo "develop change" >> develop.txt
git add develop.txt
git commit --quiet -m "Add develop change"
git push -u origin develop --quiet
git checkout main --quiet
git merge --no-ff develop --quiet -m "Merge develop"
git push origin main --quiet

# A genuinely disposable, ancestry-merged feature branch alongside it, so the
# plan has to distinguish "merged and protected" from "merged and disposable."
git checkout -b feature/small-fix --quiet
echo "small fix" >> fix.txt
git add fix.txt
git commit --quiet -m "Small fix"
git push -u origin feature/small-fix --quiet
git checkout main --quiet
git merge --no-ff feature/small-fix --quiet -m "Merge feature/small-fix"
git push origin main --quiet

git checkout main --quiet
