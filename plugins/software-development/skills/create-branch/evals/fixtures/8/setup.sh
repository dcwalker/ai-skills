#!/usr/bin/env bash
# No origin remote configured at all -- the skill should create the local
# branch and skip publishing silently, without treating it as an error.
set -euo pipefail
WORKSPACE_DIR="$1"
cd "$WORKSPACE_DIR"
# Intentionally no remote configured.
