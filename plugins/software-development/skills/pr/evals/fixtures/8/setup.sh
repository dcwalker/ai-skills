#!/usr/bin/env bash
# Existing draft PR; the user wants it marked ready for review.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 130-add-rate-limiting --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"></div>";
}

export function isRateLimited(requestCount: number, limit = 100): boolean {
  return requestCount > limit;
}
EOF
git add src/app.ts
git commit --quiet -m "Add basic rate limiting (#130)"
