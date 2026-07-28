#!/usr/bin/env bash
# Adds a new user-facing CLI flag but leaves README.md (which documents the
# CLI's flags) unchanged. The skill should notice the docs are stale.
set -euo pipefail
cd "$1"

git checkout -b PROJ-404-add-export-csv-flag --quiet

cat > src/cli.ts <<'EOF'
export const FLAGS = ["--help", "--version", "--export-csv"];
EOF
