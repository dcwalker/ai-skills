#!/usr/bin/env bash
# PR #42: one unresolved review comment that legitimately spans two files --
# both src/order-total.js and src/format.js hardcode a 7% tax rate instead of
# using the shared TAX_RATE constant in src/constants.js. This should become
# one commit touching both files, referencing the single PR comment it
# addresses.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b order-total-tax --quiet
