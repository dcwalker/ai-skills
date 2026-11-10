#!/usr/bin/env bash
# old-blog's folder is gone. -projects-mystery has a transcript that records no cwd, so
# its path is unknown and it must be kept. recipe-app is live.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app"
transcripts -projects-old-blog "$RUN_DIR/projects/old-blog" 2
