#!/usr/bin/env bash
# origin's main has advanced beyond the local main (simulating teammates'
# merges). The user explicitly asks for the new branch to be based on the
# latest main, so the skill is expected to fetch/pull before branching.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet

# Advance origin's main independently via a throwaway clone, without
# updating the local repo's main or its origin/main tracking ref.
CLONE_DIR="$(mktemp -d)"
git clone --quiet "$ORIGIN_DIR" "$CLONE_DIR"
(
  cd "$CLONE_DIR"
  git config user.name "Eval Fixture"
  git config user.email "eval-fixture@localhost"
  git config commit.gpgsign false
  echo "marker" > LATEST_MARKER.txt
  git add LATEST_MARKER.txt
  git commit --quiet -m "A teammate's merge that landed after this workspace was cloned"
  git push --quiet origin main
)
rm -rf "$CLONE_DIR"
