#!/usr/bin/env bash
# Clean, single-concern diff on a branch with no derivable issue key.
set -euo pipefail
cd "$1"

git checkout -b quick-fix --quiet

cat > src/utils.ts <<'EOF'
export function formatBytes(bytes: number): string {
  if (bytes >= 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${bytes} B`;
}
EOF
