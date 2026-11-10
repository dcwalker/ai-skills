#!/usr/bin/env bash
# old-blog's folder is gone; it has two transcripts, a session side file, and memory/.
# ~/.claude.json (written here, with this run's paths) has entries for recipe-app (live),
# old-blog, and a deleted worktree. Runs with "claude_config": "separate".
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../../fixture-lib.sh" "$1"
mkdir -p "$RUN_DIR/projects/recipe-app"
transcripts -projects-recipe-app "$RUN_DIR/projects/recipe-app"
transcripts -projects-old-blog "$RUN_DIR/projects/old-blog" 2
printf '{}\n' > "$PROJECTS/-projects-old-blog/00000001-0000-4000-8000-000000000001.desktop-released.json"
python3 - "$RUN_DIR" "$RUN_DIR/home/.claude.json" <<'PY'
import json, os, sys
run, target = sys.argv[1], sys.argv[2]
data = {"numStartups": 12, "theme": "dark", "projects": {
    os.path.join(run, "projects", "recipe-app"): {"allowedTools": ["Bash(npm test)"]},
    os.path.join(run, "projects", "old-blog"): {"allowedTools": []},
    os.path.join(run, "projects", "old-site", ".claude", "worktrees", "brave-hopper-1a2b3c"): {}}}
os.makedirs(os.path.dirname(target), exist_ok=True)
with open(target, "w") as handle:
    json.dump(data, handle, indent=2)
os.chmod(target, 0o600)
PY
