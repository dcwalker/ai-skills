#!/usr/bin/env bash
# Feature branch with a single clear change, no ticket reference, no PR
# yet. The user's prompt gives no title -- the skill must still produce a
# specific, outcome-based one.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b improve-error-toast --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"><div id=\"toast\"></div></div>";
}

export function showErrorToast(message: string, autoDismissMs = 4000): void {
  const el = document.getElementById("toast");
  if (!el) return;
  el.textContent = message;
  setTimeout(() => {
    el.textContent = "";
  }, autoDismissMs);
}
EOF
git add src/app.ts
git commit --quiet -m "Add auto-dismiss timer to error toast"
