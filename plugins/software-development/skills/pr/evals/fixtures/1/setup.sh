#!/usr/bin/env bash
# Feature branch with committed work referencing GitHub issue #42, no PR
# exists yet for it. gh-cassette.json makes `gh pr view`/`gh pr list` report
# no existing PR and captures `gh pr create` and `gh issue view 42`.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"

ORIGIN_DIR="$(dirname "$WORKSPACE_DIR")/origin.git"
git init --bare --quiet "$ORIGIN_DIR"
git remote add origin "$ORIGIN_DIR"
git push -u origin main --quiet
git remote set-head origin -a
git remote set-url origin https://github.com/example-org/demo-app.git

git checkout -b 42-add-csv-export-button --quiet

cat > src/app.ts <<'EOF'
export function renderApp(): string {
  return "<div id=\"app\"><button id=\"export-csv\">Export CSV</button></div>";
}

export function exportCsv(rows: string[][]): string {
  return rows.map((row) => row.join(",")).join("\n");
}
EOF
git add src/app.ts
git commit --quiet -m "Add CSV export button (#42)"

mkdir -p tests
cat > tests/app.test.ts <<'EOF'
import { exportCsv } from "../src/app";

test("exportCsv joins rows with commas", () => {
  expect(exportCsv([["a", "b"]])).toBe("a,b");
});
EOF
git add tests/app.test.ts
git commit --quiet -m "Add tests for CSV export"
