#!/usr/bin/env bash
# PR #42: no unresolved comments at all (the cassette's reviewThreads list is
# empty). The correct behavior is a clean report of nothing to do -- no
# fixes, no replies, no resolve calls.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b checkout-flow --quiet
