#!/usr/bin/env bash
# Two stashes with opposite correct outcomes:
#   stash@{1} (created first, on main): a parser fix that was SUBSEQUENTLY
#             committed to main in equivalent form -- superseded, safe to drop.
#   stash@{0} (created second, on feature/report-export): polish belonging to
#             a live, unmerged branch -- still relevant, must be kept.
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-11.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

# --- Stash 1: fix made, stashed, then the same fix landed on main anyway ---
cat > src/parser.js <<'EOF'
function parseCsvLine(line) {
  const cells = line.split(',');
  return cells;
}

function parseCsv(text) {
  return text.split('\n').filter(Boolean).map(parseCsvLine);
}

module.exports = { parseCsv, parseCsvLine };
EOF
git stash push -m "fix parseCsvLine dropping the last cell" --quiet

# The equivalent fix lands on main directly (as if a teammate or a later
# session fixed it), superseding the stash:
cat > src/parser.js <<'EOF'
function parseCsvLine(line) {
  const cells = line.split(',');
  return cells;
}

function parseCsv(text) {
  return text.split('\n').filter(Boolean).map(parseCsvLine);
}

module.exports = { parseCsv, parseCsvLine };
EOF
git add src/parser.js
git commit --quiet -m "Fix parseCsvLine dropping the last cell of every row"
git push origin main --quiet

# --- Stash 0: WIP belonging to a live, unmerged feature branch ---
git checkout -b feature/report-export --quiet
cat > src/export.js <<'EOF'
function exportReport(rows) {
  return rows.map((r) => r.join('\t')).join('\n');
}

module.exports = { exportReport };
EOF
git add src/export.js
git commit --quiet -m "Start report export module"
git push -u origin feature/report-export --quiet

echo "// TODO: add CSV quoting support before release" >> src/export.js
git stash push -m "WIP report export quoting" --quiet

git checkout main --quiet
