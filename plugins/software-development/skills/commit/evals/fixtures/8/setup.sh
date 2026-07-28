#!/usr/bin/env bash
# Branch exists but the working tree is entirely clean -- nothing to commit.
set -euo pipefail
cd "$1"

git checkout -b PROJ-402-noop --quiet
