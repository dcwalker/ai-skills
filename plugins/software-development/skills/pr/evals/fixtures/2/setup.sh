#!/usr/bin/env bash
# Feature branch that already has an open PR. gh-cassette.json makes
# `gh pr view` report an existing PR, so the skill should edit it rather
# than create a duplicate.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 77-fix-nav-highlight --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"><nav class=\"active\"></nav></div>";
}

export function highlightActiveNavItem(path: string, current: string): boolean {
  return path === current;
}
EOF
git add src/app.ts
git commit --quiet -m "Fix nav item not highlighting on nested routes (#77)"
