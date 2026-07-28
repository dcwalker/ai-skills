#!/usr/bin/env bash
# The project's lint script passes cleanly; a clean single-concern diff
# should be committed normally with no WIP prefix.
set -euo pipefail
cd "$1"

git checkout -b PROJ-401-update-copy --quiet

cat > src/copy.ts <<'EOF'
export const WELCOME_MESSAGE = "Welcome back!";
EOF
