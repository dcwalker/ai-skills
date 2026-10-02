#!/usr/bin/env bash
# A Python repo with no Xcode project. Its merged feature/rename-greeting
# branch is still checked out in a worktree at ../wt-rename, and the trial's
# private HOME holds Xcode DerivedData for other projects only, at
# ../home/Library/Developer/Xcode/DerivedData:
#   Gadget-eqwr...  another project, WorkspacePath missing   -> untouched
#   Gadget-fzxc...  another project, WorkspacePath exists    -> untouched
#   ModuleCache.noindex  Xcode's shared cache                -> untouched
# The build-cache section of the plan is N/A: no folder points into this
# repo's worktrees, and the repo tracks no .xcodeproj or .xcworkspace to
# attribute the stale one to.
set -euo pipefail
WORKSPACE_DIR="$(cd "$1" && pwd -P)"
RUN_DIR="$(cd "$WORKSPACE_DIR/.." && pwd -P)"
BARE_DIR="$RUN_DIR/origin-17.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/rename-greeting --quiet
cat > app.py <<'PY'
def greet(name):
    return f"Hi, {name}!"
PY
git add app.py
git commit --quiet -m "Shorten the greeting"
git push -u origin feature/rename-greeting --quiet
git checkout main --quiet
git merge --no-ff feature/rename-greeting --quiet -m "Merge feature/rename-greeting"
git push origin main --quiet
git worktree add --quiet "$RUN_DIR/wt-rename" feature/rename-greeting

mkdir -p "$RUN_DIR/gadget-app/Gadget.xcodeproj"

DERIVED_DATA="$RUN_DIR/home/Library/Developer/Xcode/DerivedData"
for ENTRY in \
  "Gadget-eqwrtzuiopasdfghjklyxcvbnmeu:$RUN_DIR/gadget/Gadget.xcodeproj" \
  "Gadget-fzxcvbnmlkjhgfdsaqwertyuiopaa:$RUN_DIR/gadget-app/Gadget.xcodeproj"; do
  FOLDER="$DERIVED_DATA/${ENTRY%%:*}"
  mkdir -p "$FOLDER/Build/Products/Debug"
  head -c 1048576 /dev/zero > "$FOLDER/Build/Products/Debug/Gadget"
  plutil -create xml1 "$FOLDER/info.plist"
  plutil -insert WorkspacePath -string "${ENTRY#*:}" "$FOLDER/info.plist"
done

git checkout main --quiet
