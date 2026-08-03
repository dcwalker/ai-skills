#!/usr/bin/env bash
# Two open Dependabot PRs (#301 axios, #302 left-pad), both direct
# dependencies with patch-level bumps. Each PR carries its own html_url, so
# the trial can grade whether the plan and the Step 8 report cite the PRs as
# links rather than as bare numbers.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/webapp.git
git checkout -b chore-deps --quiet
