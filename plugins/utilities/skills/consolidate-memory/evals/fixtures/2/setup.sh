#!/usr/bin/env bash
# recipe-app holds a memory calling Robin Sam's cousin, while the tree's people/robin.md
# says sister, plus a clean universal email preference.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app" "$RUN_DIR/projects/garden-planner"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app" 2
transcripts -projects-garden-planner "$RUN_DIR/projects/garden-planner"
