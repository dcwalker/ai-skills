#!/usr/bin/env bash
# PR #42: two unresolved review comments -- one from a bot (lint-bot[bot]),
# pointing at a real bug (unhandled JSON.parse exception), and one from a
# human reviewer that is just an open question about future scope. The user
# will ask to process only bot comments (--bots), so only the bot's comment
# should be fixed/committed/resolved; the human's comment must be left
# untouched.
set -euo pipefail
cd "$1"

git remote add origin https://github.com/acme/widgets.git
git checkout -b parse-config --quiet
