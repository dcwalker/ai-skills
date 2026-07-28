#!/usr/bin/env bash
# A single, small, self-contained change -- the description body should end
# up with 3 or fewer bullet points, so the tl;dr line should be omitted.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b tweak-button-padding --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"><button style=\"padding: 12px 20px\">Save</button></div>";
}
EOF
git add src/app.ts
git commit --quiet -m "Increase Save button padding for easier tapping on mobile"
