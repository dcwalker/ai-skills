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
# Usage: bash plugins/life-skills/skills/triage/evals/run-trials.sh [id ...]
# Run from the repo root. With no arguments, wipes .trial-runs/ and runs
# every eval in evals.json. With explicit ids (e.g. `run-trials.sh 6 7 8 9`
# after a partial run died on a session limit), re-runs only those,
# replacing just their own .trial-runs/<id>/ dirs and leaving completed
# trials in place.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." > /dev/null && pwd)"
TRIALS_DIR="$SCRIPT_DIR/.trial-runs"

if [[ $# -gt 0 ]]; then
  IDS="$*"
  for ID in $IDS; do
    rm -rf "$TRIALS_DIR/$ID"
  done
else
  IDS=$(python3 -c "
import json
data = json.load(open('$SCRIPT_DIR/evals.json'))
print(' '.join(str(e['id']) for e in data['evals']))
")
  rm -rf "$TRIALS_DIR"
fi
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
  # `|| true`: a failing trial (session limit hit, transient API error, a
  # result that reports is_error) must not abort the batch under set -e --
  # its result.json still lands in its own $RUN_DIR and the failure shows
  # up in metrics.json's is_error/parse_error fields for the grader.
  (
    cd "$WORKSPACE_DIR"
    claude -p --dangerously-skip-permissions --strict-mcp-config \
      --mcp-config "$MCP_CONFIG_PATH" --output-format json -- "$PROMPT"
  ) > "$RUN_DIR/result.json" 2> "$RUN_DIR/stderr.txt" || \
    echo "  WARNING: claude exited non-zero for eval $ID; continuing with the next eval"

  # A parse failure must stay isolated to this one trial: under set -e an
  # uncaught exception here would abort the whole batch, losing every eval
  # ID not yet run. Each trial's artifacts live in their own $RUN_DIR, so a
  # bad result.json just gets a placeholder metrics.json and the loop moves
  # on; the raw result.json is kept for manual inspection.
  python3 - "$RUN_DIR" <<'PYEOF'
import json, sys
run_dir = sys.argv[1]
try:
    with open(f"{run_dir}/result.json") as f:
        data = json.load(f)
except (json.JSONDecodeError, OSError) as e:
    with open(f"{run_dir}/metrics.json", "w") as f:
        json.dump({"parse_error": str(e),
                   "note": "result.json was missing or not valid JSON; "
                           "inspect it manually alongside stderr.txt"}, f, indent=2)
    print(f"  WARNING: could not parse result.json ({e}); wrote placeholder "
          "metrics.json and continuing with the next eval")
    sys.exit(0)
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
