#!/usr/bin/env bash
# old-blog's folder is gone. -projects-mystery has a transcript that records no cwd, so
# its path is unknown and it must be kept. recipe-app is live. photo-archive was on an external
# drive that is not mounted, so it must be kept too.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app"
transcripts -projects-old-blog "$RUN_DIR/projects/old-blog" 2
transcripts -Volumes-Archive-Drive-photo-archive "/Volumes/Consolidate Memory Eval Drive/photo-archive"
