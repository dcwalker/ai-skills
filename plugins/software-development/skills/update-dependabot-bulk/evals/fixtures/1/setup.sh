#!/usr/bin/env bash
# Two open Dependabot PRs bumping direct dependencies (lodash, chalk) with patch-level version bumps only -- no majors.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps --quiet
