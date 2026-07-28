#!/usr/bin/env bash
# Two open, safe direct-dependency Dependabot PRs (lodash, chalk). The user prompt does not pre-approve applying updates, so the skill must present a plan and ask before writing any files.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-gate --quiet
