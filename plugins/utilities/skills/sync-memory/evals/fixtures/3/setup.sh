#!/usr/bin/env bash
# old-blog's folder is gone (dead), with two transcripts, a session directory, and a
# memory/ overview. recipe-app is live. A scratch eval workspace under tmp-workspace/
# still exists, so it is live too, however temporary it looks.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app" "$RUN_DIR/tmp-workspace/eval-7/workspace"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app" 2
transcripts -projects-old-blog "$RUN_DIR/projects/old-blog" 2
session_dir -projects-old-blog
transcripts -tmp-workspace-eval-7-workspace "$RUN_DIR/tmp-workspace/eval-7/workspace"
