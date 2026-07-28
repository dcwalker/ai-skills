#!/usr/bin/env bash
# PR #42: two unresolved review comments on the same file -- one valid
# (reserveStock mutates its input in place, surprising callers) and one
# invalid (a request to rename the function to snake_case, which doesn't
# match this JS codebase's conventions). Both must be handled, independently:
# the valid one fixed and committed, the invalid one replied-to and resolved
# without a code change.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b inventory-reserve --quiet
