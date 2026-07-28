#!/usr/bin/env bash
# Two open Dependabot PRs: a safe lodash patch bump, and an axios major version bump (0.27.2 -> 1.6.0) that likely carries breaking changes.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-major --quiet
