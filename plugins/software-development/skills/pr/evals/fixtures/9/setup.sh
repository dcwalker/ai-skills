#!/usr/bin/env bash
# Existing PR with no assignees; the user agrees to be assigned when asked.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 140-add-request-logging --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"></div>";
}

export function logRequest(method: string, path: string): string {
  return `${method} ${path}`;
}
EOF
git add src/app.ts
git commit --quiet -m "Add request logging middleware (#140)"
