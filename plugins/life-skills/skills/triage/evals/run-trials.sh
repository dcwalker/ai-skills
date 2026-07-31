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

  # JSON output mode captures the subprocess's own wall-clock duration and
  # real token usage alongside the reply -- plain-text mode reports neither,
  # which left earlier baselines approximating time from file mtimes with no
  # token figures at all. result.json keeps the full envelope; transcript.txt
  # stays the human-readable reply for graders.
  (
    cd "$WORKSPACE_DIR"
    claude -p --dangerously-skip-permissions --strict-mcp-config \
      --mcp-config "$MCP_CONFIG_PATH" --output-format json -- "$PROMPT"
  ) > "$RUN_DIR/result.json" 2> "$RUN_DIR/stderr.txt"

  python3 - "$RUN_DIR" <<'PYEOF'
import json, sys
run_dir = sys.argv[1]
with open(f"{run_dir}/result.json") as f:
    data = json.load(f)
with open(f"{run_dir}/transcript.txt", "w") as f:
    f.write(data.get("result", ""))
usage = data.get("usage", {})
metrics = {
    "duration_seconds": round(data.get("duration_ms", 0) / 1000, 3),
    "duration_api_seconds": round(data.get("duration_api_ms", 0) / 1000, 3),
    "num_turns": data.get("num_turns"),
    "total_cost_usd": data.get("total_cost_usd"),
    "tokens": {
        "input": usage.get("input_tokens"),
        "output": usage.get("output_tokens"),
        "cache_creation_input": usage.get("cache_creation_input_tokens"),
        "cache_read_input": usage.get("cache_read_input_tokens"),
    },
    "is_error": data.get("is_error"),
}
with open(f"{run_dir}/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
print(f"  duration: {metrics['duration_seconds']}s, "
      f"tokens in/out: {metrics['tokens']['input']}/{metrics['tokens']['output']}, "
      f"cache read: {metrics['tokens']['cache_read_input']}")
PYEOF

  echo "  -> saved to $RUN_DIR"
  echo
done

echo "All trials complete. Review $TRIALS_DIR/<id>/: transcript.txt, metrics.json,"
echo "and the per-service <service>-state-out.json / <service>-calls.log files."
