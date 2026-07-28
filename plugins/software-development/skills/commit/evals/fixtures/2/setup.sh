#!/usr/bin/env bash
# Clean, single-concern diff on a branch with a derivable GitHub issue number.
set -euo pipefail
cd "$1"

git checkout -b 42-fix-login-redirect --quiet

cat > src/routes.ts <<'EOF'
export function resolveRedirect(path: string): string {
  if (path === "/old-login" || path === "/login-legacy") {
    return "/login";
  }
  return path;
}
EOF
