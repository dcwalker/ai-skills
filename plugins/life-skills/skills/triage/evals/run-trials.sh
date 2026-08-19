#!/usr/bin/env bash
# One-time local driver for triage's MCP-backed eval trials. Not part of the
# eval harness proper (that's evals/lib/run-mcp-eval.sh) -- this just loops
# over evals.json's ids, runs each as a real `claude -p --strict-mcp-config`
# subprocess against the Trello stub, and saves everything needed to grade
# the trial (transcript, final state, call log) into .trial-runs/<id>/,
# gitignored so this never gets committed.
#
# The nested `claude` subprocess inherits the parent session's credentials,
# so this does run when delegated to an in-session Bash tool call. If it does
# not authenticate in whatever sandbox you are in, run it from a normal
# logged-in terminal instead. See evals/README.md's "MCP stub servers"
# section for the underlying mechanism.
#
# Usage: bash plugins/life-skills/skills/triage/evals/run-trials.sh [id ...]
# Run from the repo root. Set TRIALS_DIR to write the trials somewhere else. With no arguments, wipes .trial-runs/ and runs
# every eval in evals.json. With explicit ids (e.g. `run-trials.sh 6 7 8 9`
# after a partial run died on a session limit), re-runs only those,
# replacing just their own .trial-runs/<id>/ dirs and leaving completed
# trials in place.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." > /dev/null && pwd)"
# Default output lives beside the evals, gitignored. Override it to put the
# trial workspaces outside the repo: a workspace under evals/ leaves
# evals.json and fixtures/ three directories up from the trial's own cwd,
# within reach of an executor that goes looking, and that is the answer key.
TRIALS_DIR="${TRIALS_DIR:-$SCRIPT_DIR/.trial-runs}"

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

  # An explicit allowlist rather than --dangerously-skip-permissions, matching
  # evals/lib/run-mcp-trials.sh: that flag is refused outright when the shell
  # is root, which rules out containers and CI, and an allowlist keeps the
  # trial's tool surface auditable. One unconditional path rather than a
  # root-only branch, so the surface cannot silently differ between the
  # environment a baseline was recorded in and the one it is reproduced in.
  #
  # The non-MCP tools are load-bearing, not filler: Step 1 and Step 4c each
  # define an MCP -> skill -> CLI -> REST hierarchy, and run-mcp-eval.sh
  # deliberately isolates the two shell paths triage/SKILL.md names (curl to
  # Jira's REST API, and gh) by scrubbing credentials and shadowing gh, so
  # those tiers are meant to be exercisable in a trial. Without Bash they can
  # never fire. Every stub server is allowed wholesale, including its write
  # tools, so that "the skill wrote nothing" stays a finding about the skill
  # rather than an artifact of the harness blocking the call. Servers come
  # from this fixture's own mcp-config.json, so a fixture that wires up a new
  # service is covered without editing this list.
  mapfile -t PERM_ARGS < <(python3 -c "
import json
config = json.load(open('$MCP_CONFIG_PATH'))
print('--allowedTools')
print('Bash Read Write Edit Glob Grep WebFetch TodoWrite Skill '
      + ' '.join('mcp__' + s for s in config['mcpServers']))
")

  # The subprocess runs with cwd inside $WORKSPACE_DIR, where nothing loads
  # this repo's plugins, so without staging the skill the trial would measure
  # the bare model. Stage SKILL.md and references/ and nothing else: a
  # whole-directory copy would put evals.json and the fixtures inside the
  # workspace, handing the trial its own answer key, while SKILL.md alone
  # would leave every references/ link in it dangling and silently drop the
  # material those links carry.
  mkdir -p "$WORKSPACE_DIR/.claude/skills/triage"
  cp "$SCRIPT_DIR/../SKILL.md" "$WORKSPACE_DIR/.claude/skills/triage/SKILL.md"
  if [[ -d "$SCRIPT_DIR/../references" ]]; then
    cp -R "$SCRIPT_DIR/../references" "$WORKSPACE_DIR/.claude/skills/triage/"
  fi

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
    claude -p "${PERM_ARGS[@]}" --strict-mcp-config \
      --mcp-config "$MCP_CONFIG_PATH" --output-format json -- "$PROMPT" \
      < /dev/null
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
