#!/usr/bin/env bash
# A single open Dependabot PR bumping a direct dependency (chalk) with a patch-level version change.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-single --quiet
