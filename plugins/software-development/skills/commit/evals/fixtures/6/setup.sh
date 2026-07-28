#!/usr/bin/env bash
# The project's lint script is broken (always fails, pre-existing and
# unrelated to this diff), so the skill must attempt a fix or ask before
# committing this otherwise-clean change.
set -euo pipefail
cd "$1"

git checkout -b PROJ-400-add-validation --quiet

cat > src/validate.ts <<'EOF'
export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
EOF
