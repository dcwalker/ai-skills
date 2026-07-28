#!/usr/bin/env bash
# Repo has a long PR template (30+ lines). No PR exists yet.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 110-add-bulk-delete --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"><button id=\"bulk-delete\">Delete selected</button></div>";
}

export function bulkDelete(ids: string[], deleteFn: (id: string) => void): void {
  ids.forEach(deleteFn);
}
EOF
git add src/app.ts
git commit --quiet -m "Add bulk delete for selected items (#110)"
