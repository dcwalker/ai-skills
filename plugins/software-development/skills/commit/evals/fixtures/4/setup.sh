#!/usr/bin/env bash
# Diff spans two unrelated concerns: an auth bugfix and an unrelated
# dependency bump in package.json.
set -euo pipefail
cd "$1"

git checkout -b PROJ-301-fix-auth-bug --quiet

cat > src/auth.ts <<'EOF'
export function login(username: string, password: string): boolean {
  if (!username || !password) {
    return false;
  }
  return checkCredentials(username.trim(), password);
}

function checkCredentials(username: string, password: string): boolean {
  return username === password;
}
EOF

cat > package.json <<'EOF'
{
  "name": "demo-app",
  "version": "1.0.0",
  "dependencies": {
    "left-pad": "1.3.0"
  }
}
EOF

cat > package-lock.json <<'EOF'
{
  "name": "demo-app",
  "version": "1.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "demo-app",
      "version": "1.0.0",
      "dependencies": {
        "left-pad": "1.3.0"
      }
    },
    "node_modules/left-pad": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/left-pad/-/left-pad-1.3.0.tgz",
      "integrity": "sha512-000000000000000000000000000000000000000000000000000000000000000000000000000000000000A="
    }
  }
}
EOF
