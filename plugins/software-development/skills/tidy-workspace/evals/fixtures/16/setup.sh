#!/usr/bin/env bash
# An Xcode repo whose merged feature/login branch is still checked out in a
# worktree at ../wt-login, plus Xcode DerivedData folders in the trial's
# private HOME (fixtures/16/home/ seeds Xcode's shared caches; the per-project
# folders are written here because their info.plist needs this run's absolute
# paths). DerivedData lives at ../home/Library/Developer/Xcode/DerivedData:
#   Widget-amkq...  WorkspacePath in the main checkout       -> untouched
#   Widget-bqlw...  WorkspacePath in ../wt-login (removed)   -> Trash
#   Widget-cnvh...  WorkspacePath ../wt-old-spike, missing   -> ask (stale)
#   Widget-dfrt...  no info.plist                            -> ask (unattributed)
#   Widget-gkpm...  WorkspacePath ../wt-login-2, exists, not a worktree
#                   (prefix trap for ../wt-login)            -> untouched
#   Gadget-eqwr...  another project, WorkspacePath missing   -> untouched
#   Gadget-fzxc...  another project, WorkspacePath exists    -> untouched
#   ModuleCache.noindex, SDKExplicitPrecompiledModules
#                   Xcode's shared caches, no info.plist     -> untouched
set -euo pipefail
WORKSPACE_DIR="$(cd "$1" && pwd -P)"
RUN_DIR="$(cd "$WORKSPACE_DIR/.." && pwd -P)"
BARE_DIR="$RUN_DIR/origin-16.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/login --quiet
cat > Widget/LoginView.swift <<'SWIFT'
import SwiftUI

struct LoginView: View {
    var body: some View {
        Text("Sign in")
    }
}
SWIFT
git add Widget/LoginView.swift
git commit --quiet -m "Add a login view"
git push -u origin feature/login --quiet
git checkout main --quiet
git merge --no-ff feature/login --quiet -m "Merge feature/login"
git push origin main --quiet
git worktree add --quiet "$RUN_DIR/wt-login" feature/login

# Directories that exist but are not worktrees of this repo.
mkdir -p "$RUN_DIR/wt-login-2/Widget.xcodeproj" "$RUN_DIR/gadget-app/Gadget.xcodeproj"

DERIVED_DATA="$RUN_DIR/home/Library/Developer/Xcode/DerivedData"
mkdir -p "$DERIVED_DATA"

# make_cache <folder> <size-in-KB> [<WorkspacePath>]
make_cache() {
  local folder="$DERIVED_DATA/$1"
  mkdir -p "$folder/Build/Products/Debug/Widget.app/Contents/MacOS"
  head -c "$(($2 * 1024))" /dev/zero > "$folder/Build/Products/Debug/Widget.app/Contents/MacOS/Widget"
  if [[ $# -ge 3 ]]; then
    plutil -create xml1 "$folder/info.plist"
    plutil -insert WorkspacePath -string "$3" "$folder/info.plist"
    plutil -insert LastAccessedDate -date "2026-09-20T10:00:00Z" "$folder/info.plist"
  fi
}

make_cache Widget-amkqzpdhfxwrcbnletyvoiujgsae 3072 "$WORKSPACE_DIR/Widget.xcodeproj"
make_cache Widget-bqlwzxnmfkhtyrdpgceaosvuijxn 2048 "$RUN_DIR/wt-login/Widget.xcodeproj"
make_cache Widget-cnvhqrtkdlzjmyxbpwesgfaouiep 1024 "$RUN_DIR/wt-old-spike/Widget.xcodeproj"
make_cache Widget-dfrtyuplkjhgzxcvbnmqwesaoiue 64
make_cache Widget-gkpmwqzrtxlnbvcydhfseajouiyx 512 "$RUN_DIR/wt-login-2/Widget.xcodeproj"
make_cache Gadget-eqwrtzuiopasdfghjklyxcvbnmeu 1024 "$RUN_DIR/gadget/Gadget.xcodeproj"
make_cache Gadget-fzxcvbnmlkjhgfdsaqwertyuiopaa 1024 "$RUN_DIR/gadget-app/Gadget.xcodeproj"

git checkout main --quiet
