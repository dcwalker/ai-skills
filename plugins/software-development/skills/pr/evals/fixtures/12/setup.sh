#!/usr/bin/env bash
# Branch name and commit messages have no ticket/issue reference anywhere.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b improve-loading-spinner-animation --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"><div id=\"spinner\" class=\"spin-smooth\"></div></div>";
}
EOF
git add src/app.ts
git commit --quiet -m "Smooth out the loading spinner animation easing curve"
