#!/usr/bin/env bash
# New PR scenario used to test declining the assignment-confirmation step.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 121-add-light-mode --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\" class=\"theme-dark\"></div>";
}

export function toggleLightMode(current: string): string {
  return current === "theme-dark" ? "theme-light" : "theme-dark";
}
EOF
git add src/app.ts
git commit --quiet -m "Add light mode toggle (#121)"
