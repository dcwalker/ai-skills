#!/usr/bin/env bash
# PR #42: one open, unresolved review comment about a missing `@` check in
# validateEmail. The branch already contains a later commit that fixes
# exactly this, so the correct handling is "already fixed": reply citing the
# existing commit SHA and resolve, with no new commit created.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b fix-email-validation --quiet

cat > src/validate.js <<'EOF'
function validateEmail(value) {
  return typeof value === 'string' && value.includes('@');
}

module.exports = { validateEmail };
EOF

git add src/validate.js
git commit --quiet -m "Require an @ symbol in validateEmail"
