#!/usr/bin/env bash
# old-blog's folder is gone. The sandbox can't run ps, so the script can't check for
# other Claude sessions and refuses unless told to ignore them, which the user never
# said. Runs with "claude_config": "separate".
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app"
transcripts -projects-old-blog "$RUN_DIR/projects/old-blog" 2
