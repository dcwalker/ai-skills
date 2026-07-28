#!/usr/bin/env bash
# Clean, single-concern diff on a branch with a derivable Jira issue key.
set -euo pipefail
cd "$1"

git checkout -b PROJ-123-fix-login-timeout --quiet

cat > src/auth.ts <<'EOF'
export const SESSION_TIMEOUT_MS = 30000;

export function login(username: string, password: string): boolean {
  if (!username || !password) {
    return false;
  }
  return checkCredentials(username, password);
}

function checkCredentials(username: string, password: string): boolean {
  return username === password;
}
EOF
