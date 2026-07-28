#!/usr/bin/env bash
# Two open Dependabot PRs touching two different package.json files: the root package.json (chalk) and a nested static/package.json (react), exercising multi-file plan handling.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-monorepo --quiet
