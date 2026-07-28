#!/usr/bin/env bash
# PR #42: the only review thread on this PR is already resolved (the
# cassette marks it isResolved: true), and this branch already contains a
# later commit that adds the null check the thread was about. list-pr-
# comments.sh's default listing excludes resolved threads, so nothing should
# show up as needing action -- the correct behavior is a clean "nothing to
# do" report, with no new commits and no reply/resolve calls.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b checkout-null-guard --quiet

cat > src/checkout.js <<'EOF'
function checkout(cart) {
  if (!cart || !cart.items || cart.items.length === 0) {
    throw new Error('Cart is empty');
  }
  return cart.items.reduce((sum, item) => sum + item.price, 0);
}

module.exports = { checkout };
EOF

git add src/checkout.js
git commit --quiet -m "Add null guard to checkout cart validation"
