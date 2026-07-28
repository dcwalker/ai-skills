#!/usr/bin/env bash
# PR #42: one open, unresolved review comment pointing at a real off-by-one
# bug in src/discount.js (loop runs one iteration past the end of the array,
# producing an undefined item and an incorrect discounted total).
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b fix-discount-loop --quiet
