#!/usr/bin/env bash
# No open Dependabot PRs -- only an unrelated human-authored PR is open, to confirm the skill filters correctly.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-none --quiet
