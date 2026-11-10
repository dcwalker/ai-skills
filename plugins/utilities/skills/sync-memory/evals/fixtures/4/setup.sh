#!/usr/bin/env bash
# No shared tree yet. The workspace holds a Claude app memory export; both live projects
# hold the duplicated ISO date preference.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app" "$RUN_DIR/projects/garden-planner"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app" 2
transcripts -projects-garden-planner "$RUN_DIR/projects/garden-planner"
