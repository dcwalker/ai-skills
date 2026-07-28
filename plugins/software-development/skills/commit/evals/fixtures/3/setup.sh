#!/usr/bin/env bash
# Otherwise-clean diff that leaves a debug console.log artifact behind.
set -euo pipefail
cd "$1"

git checkout -b PROJ-200-add-retry-logic --quiet

cat > src/network.ts <<'EOF'
export async function fetchWithRetry(url: string, attempts = 3): Promise<Response> {
  let lastError: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      console.log("HERE");
      return await fetch(url);
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError;
}
EOF
