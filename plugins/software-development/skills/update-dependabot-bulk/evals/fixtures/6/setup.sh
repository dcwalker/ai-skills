#!/usr/bin/env bash
# Five open Dependabot PRs covering all three categories at once: two safe direct bumps (lodash, chalk), a direct+transitive pair (eslint/flatted), and a major bump (axios) that should be flagged rather than silently applied.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-mixed --quiet
