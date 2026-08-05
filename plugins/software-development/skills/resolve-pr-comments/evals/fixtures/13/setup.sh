#!/usr/bin/env bash
# PR #64: two open review comments on src/discount.js, each carrying its own
# distinct comment URL -- an off-by-one loop bound and a Math.floor rounding
# call that violates CONTRIBUTING.md. Grades whether the per-comment summaries
# and the Final Report cite each comment as a link to its own URL.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b fix-cart-bugs --quiet
