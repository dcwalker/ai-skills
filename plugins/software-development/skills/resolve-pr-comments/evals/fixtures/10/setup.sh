#!/usr/bin/env bash
# PR #42: one unresolved review comment (from a security-scanning bot)
# pointing at a hardcoded Slack webhook token in src/notify.js. This is a
# real, security-sensitive bug that must be fixed and committed -- not just
# replied to -- using the existing config/secrets.js loader per
# CONTRIBUTING.md.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b notify-slack --quiet
