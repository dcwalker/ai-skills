#!/usr/bin/env bash
# One failing check whose check run reports no URL at all (html_url is null,
# so list-pr-checks.sh renders it as "N/A"). Negative counterpart to fixture
# 11: the report must not invent an actions/runs URL for a check that never
# gave one.
set -euo pipefail
cd "$1"
git remote add origin https://github.com/acme/widgets.git
