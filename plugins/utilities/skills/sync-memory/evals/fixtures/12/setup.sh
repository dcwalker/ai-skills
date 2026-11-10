#!/usr/bin/env bash
# Like eval 1, plus a one-line preference and a fact about a person in recipe-app, and
# garden-planner's MEMORY.md has a dangling link and is missing one file. Runs with
# "claude_config": "separate", so writes under ~/.claude succeed.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app" "$RUN_DIR/projects/garden-planner"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app" 2
transcripts -projects-garden-planner "$RUN_DIR/projects/garden-planner"
