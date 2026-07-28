#!/usr/bin/env bash
# One open Dependabot PR bumping a transitive dependency (minimist, pulled in only by a stale internal devDependency) for which no newer version of the parent package resolves it to the target version.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-unresolvable-transitive --quiet
