#!/usr/bin/env bash
# PR #42: one unresolved review comment asking to floor the final price to a
# whole dollar amount. CONTRIBUTING.md explicitly forbids flooring/truncating
# pricing logic in a way that overcharges a customer, and Math.round (unlike
# Math.floor) doesn't do that -- so this request conflicts with a documented
# project convention. Correct handling is a polite reply explaining why the
# current rounding is intentional, and resolving without a code change.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b pricing-rounding --quiet
