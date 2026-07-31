#!/usr/bin/env bash
# Leave an UNCOMMITTED modification to src/report.js only -- the repo also
# contains a skill directory, but the diff does not touch it, so Step 4b
# (Skill Quality Review) must NOT fire. The added function takes user input
# and interpolates it straight into SQL with no validation, violating
# CONTRIBUTING.md's user-input rule, so the general review still has a real
# finding to make.
set -euo pipefail
WORKSPACE_DIR="${1:-$(pwd)}"
cd "$WORKSPACE_DIR"

cat >> src/report.js <<'EOF'

function searchSummaries(term) {
  return db.query("SELECT * FROM summaries WHERE title LIKE '%" + term + "%'");
}

module.exports.searchSummaries = searchSummaries;
EOF
