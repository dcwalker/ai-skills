#!/usr/bin/env bash
# Two independent failing checks on PR #77, each reporting its own distinct
# check-run URL. Grades whether the Phase 4 report links the PR and both runs
# rather than naming them as bare numbers/names.
set -euo pipefail
cd "$1"
git remote add origin https://github.com/acme/widgets.git
