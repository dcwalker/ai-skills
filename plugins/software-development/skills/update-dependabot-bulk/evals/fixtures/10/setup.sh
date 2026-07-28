#!/usr/bin/env bash
# Two open Dependabot PRs bumping the same direct dependency (lodash) to two different target versions, as can happen when Dependabot reopens a PR after a new release.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-duplicate --quiet
