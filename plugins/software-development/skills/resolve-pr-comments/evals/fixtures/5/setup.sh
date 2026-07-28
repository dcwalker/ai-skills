#!/usr/bin/env bash
# PR #42: two unresolved review comments -- one from a bot (lint-bot[bot])
# and one from a human reviewer asking for a named export instead of a
# default export. The user will ask to process only human comments
# (--humans), so only the human's comment should be fixed/committed/
# resolved; the bot's comment must be left untouched.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b parse-config-exports --quiet
