#!/usr/bin/env bash
# Repo has a short PR template (well under 30 lines). No PR exists yet.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 101-add-search-filter --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"><input id=\"search-filter\" /></div>";
}

export function filterItems(items: string[], query: string): string[] {
  return items.filter((item) => item.toLowerCase().includes(query.toLowerCase()));
}
EOF
git add src/app.ts
git commit --quiet -m "Add search filter input (#101)"
