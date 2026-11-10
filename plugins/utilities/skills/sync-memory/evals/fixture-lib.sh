# Shared by the sync-memory fixtures' setup.sh scripts. Source it with the workspace
# directory as $1. It defines RUN_DIR, PROJECTS (the trial's private ~/.claude/projects), and:
#
#   transcripts <slug> <cwd> [count]  write session transcripts that record <cwd>, the way
#                                     Claude Code does, so the script can find the project's
#                                     real path; count defaults to 1
#   session_dir <slug>                add a UUID-named session artifact directory
#
# Transcripts are written here rather than shipped in home/ because they must record this
# run's absolute paths: a live project's path has to exist and a dead one's must not.
WORKSPACE_DIR="$(cd "$1" && pwd -P)"
RUN_DIR="$(cd "$WORKSPACE_DIR/.." && pwd -P)"
PROJECTS="$RUN_DIR/home/.claude/projects"

transcripts() {
  local slug="$1" cwd="$2" count="${3:-1}" i uuid
  mkdir -p "$PROJECTS/$slug"
  for ((i = 1; i <= count; i++)); do
    uuid="$(printf '%08d-0000-4000-8000-%012d' "$i" "$i")"
    printf '{"type":"summary","summary":"Earlier session"}\n{"type":"user","cwd":"%s","sessionId":"%s","message":{"role":"user","content":"Pick up where we left off."}}\n' \
      "$cwd" "$uuid" > "$PROJECTS/$slug/$uuid.jsonl"
  done
}

session_dir() {
  mkdir -p "$PROJECTS/$1/00000009-0000-4000-8000-000000000009/subagents"
  printf '{"type":"assistant"}\n' > "$PROJECTS/$1/00000009-0000-4000-8000-000000000009/subagents/agent.jsonl"
}
