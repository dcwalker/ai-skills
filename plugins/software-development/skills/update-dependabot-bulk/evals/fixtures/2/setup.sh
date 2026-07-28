#!/usr/bin/env bash
# Two open Dependabot PRs: a direct eslint bump, and a transitive flatted bump that eslint's newer version resolves (mirrors SKILL.md's own worked example).
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps-transitive --quiet
