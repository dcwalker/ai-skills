#!/usr/bin/env bash
# recipe-app has a memory about a launch whose date (2026-04-15) has passed and one that
# says the beta opens "next month", noted 2026-11-02. Runs with "claude_config":
# "separate", so writes under ~/.claude succeed.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app" "$RUN_DIR/projects/garden-planner"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app" 2
transcripts -projects-garden-planner "$RUN_DIR/projects/garden-planner"
