#!/usr/bin/env bash
# Two open Dependabot PRs: one (lodash) is already stale/satisfied because package.json already has the target version, and one (chalk) is a real pending bump.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-stale --quiet
