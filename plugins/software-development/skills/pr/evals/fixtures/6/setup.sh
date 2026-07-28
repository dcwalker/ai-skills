#!/usr/bin/env bash
# New PR scenario used to test the assignment-confirmation step.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 120-add-dark-mode --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\" class=\"theme-light\"></div>";
}

export function toggleDarkMode(current: string): string {
  return current === "theme-light" ? "theme-dark" : "theme-light";
}
EOF
git add src/app.ts
git commit --quiet -m "Add dark mode toggle (#120)"
