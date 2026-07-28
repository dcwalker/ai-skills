#!/usr/bin/env bash
# PR #42: one open, unresolved review comment that is a genuine clarifying
# question ("why did you do it this way?"), not an action item. The correct
# handling is a reply explaining the reasoning, not a code change.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b add-retry-throttle --quiet
