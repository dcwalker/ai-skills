#!/usr/bin/env bash
# Feature branch referencing GitHub issue #77, no PR yet. gh-cassette.json
# supplies the issue's URL and the URL `gh pr create` prints, so the trial can
# grade whether both the description and the report back to the user carry
# real hyperlinks rather than bare numbers.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
# --initial-branch=main so the bare repo's HEAD points at a ref that exists
# once main is pushed; without it `git remote set-head -a` below cannot
# determine the remote HEAD on git versions that still default to master.
git init --bare --initial-branch=main --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 77-fix-invoice-rounding --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"></div>";
}

export function formatInvoiceTotal(cents: number): string {
  return (Math.round(cents) / 100).toFixed(2);
}
EOF
git add src/app.ts
git commit --quiet -m "Round invoice totals consistently (#77)"
