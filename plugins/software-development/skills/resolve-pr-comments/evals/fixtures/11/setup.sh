#!/usr/bin/env bash
# PR #42: two unresolved, unrelated review comments on two different files --
# a loose-equality bug in src/cart.js and a divide-by-zero bug in
# src/shipping.js. Both are valid and should be fixed, but as two separate,
# well-documented commits (per CONTRIBUTING.md's "small, single-concern
# commits" guidance), not lumped into one.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b cart-and-shipping-fixes --quiet
