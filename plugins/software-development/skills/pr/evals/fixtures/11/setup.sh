#!/usr/bin/env bash
# Branch's commits reference two separate GitHub issues -- both should be
# linked in the PR description's Related section.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 160-fix-pagination-and-sorting --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"></div>";
}

export function paginate<T>(items: T[], page: number, pageSize: number): T[] {
  const start = (page - 1) * pageSize;
  return items.slice(start, start + pageSize);
}
EOF
git add src/app.ts
git commit --quiet -m "Fix off-by-one error in pagination (#10)"

cat >> src/app.ts <<'EOF'

export function sortByName<T extends { name: string }>(items: T[]): T[] {
  return [...items].sort((a, b) => a.name.localeCompare(b.name));
}
EOF
git add src/app.ts
git commit --quiet -m "Fix sort order not applying after pagination (#20)"
