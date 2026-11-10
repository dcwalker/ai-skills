#!/usr/bin/env bash
# Six projects whose folders are all gone and no live ones, which usually means the
# wrong machine or an unplugged drive. Runs with "claude_config": "separate".
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
transcripts -projects-app-1 "$RUN_DIR/projects/app-1"
transcripts -projects-app-2 "$RUN_DIR/projects/app-2"
transcripts -projects-app-3 "$RUN_DIR/projects/app-3"
transcripts -projects-app-4 "$RUN_DIR/projects/app-4"
transcripts -projects-app-5 "$RUN_DIR/projects/app-5"
transcripts -projects-app-6 "$RUN_DIR/projects/app-6"
