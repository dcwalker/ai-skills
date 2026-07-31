#!/usr/bin/env bash
# One-time local driver for triage's MCP-backed eval trials. Not part of the
# eval harness proper (that's evals/lib/run-mcp-eval.sh) -- this just loops
# over evals.json's ids, runs each as a real `claude -p --strict-mcp-config`
# subprocess against the Trello stub, and saves everything needed to grade
# the trial (transcript, final state, call log) into .trial-runs/<id>/,
# gitignored so this never gets committed.
#
# Nested `claude` subprocesses can't authenticate inside some sandboxed
# Claude Code sessions, so this has to be run from a normal logged-in
# terminal, not delegated to an in-session Bash tool call. See
# evals/README.md's "MCP stub servers" section for the underlying mechanism.
#
# Usage: bash plugins/life-skills/skills/triage/evals/run-trials.sh
# Run from the repo root.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." > /dev/null && pwd)"
TRIALS_DIR="$SCRIPT_DIR/.trial-runs"

IDS=$(python3 -c "
import json
data = json.load(open('$SCRIPT_DIR/evals.json'))
print(' '.join(str(e['id']) for e in data['evals']))
")

rm -rf "$TRIALS_DIR"
mkdir -p "$TRIALS_DIR"

for ID in $IDS; do
  PROMPT=$(python3 -c "
import json
data = json.load(open('$SCRIPT_DIR/evals.json'))
for e in data['evals']:
    if e['id'] == $ID:
        print(e['prompt'])
        break
")
  RUN_DIR="$TRIALS_DIR/$ID"
  echo "=== Eval $ID ==="
  echo "Prompt: $PROMPT"

  ENV_FILE="$("$REPO_ROOT/evals/lib/run-mcp-eval.sh" "$SCRIPT_DIR" "$ID" "$RUN_DIR")"
  # shellcheck disable=SC1090
  source "$ENV_FILE"

  (
    cd "$WORKSPACE_DIR"
    claude -p --dangerously-skip-permissions --strict-mcp-config \
      --mcp-config "$MCP_CONFIG_PATH" -- "$PROMPT"
  ) > "$RUN_DIR/transcript.txt" 2> "$RUN_DIR/stderr.txt"

  echo "  -> saved to $RUN_DIR"
  echo
done

echo "All trials complete. Review $TRIALS_DIR/<id>/{transcript.txt,trello-state-out.json,trello-calls.log}."
