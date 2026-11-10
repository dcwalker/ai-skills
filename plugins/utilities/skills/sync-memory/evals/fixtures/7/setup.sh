#!/usr/bin/env bash
# Same state as eval 1, but the user asks without authorizing changes.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app" "$RUN_DIR/projects/garden-planner"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app" 2
transcripts -projects-garden-planner "$RUN_DIR/projects/garden-planner"
