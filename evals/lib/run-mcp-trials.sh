#!/usr/bin/env bash
# Batch driver for any skill's MCP-backed eval trials. Loops over the ids in
# a skill's evals.json, runs each as a real `claude -p --strict-mcp-config`
# subprocess against the stub servers its fixture provides, and saves
# everything needed to grade the trial (transcript, metrics, final state,
# call log) into <skill-evals-dir>/.trial-runs/<id>/.
#
# The per-trial environment comes from run-mcp-eval.sh, which is the harness
# proper; this script only sequences trials and extracts metrics. triage's
# own evals/run-trials.sh predates this file and still carries its own copy
# of the loop -- reducing it to a caller of this script is a worthwhile
# follow-up, not something done here.
#
# Nested `claude` subprocesses cannot authenticate inside some sandboxed
# Claude Code sessions, so run this from a normal logged-in terminal rather
# than delegating it to an in-session Bash tool call. See evals/README.md's
# "MCP stub servers" section for the underlying mechanism.
#
# Usage: bash evals/lib/run-mcp-trials.sh <skill-evals-dir> [id ...]
#
#   bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/writing/evals
#   bash evals/lib/run-mcp-trials.sh plugins/life-skills/skills/writing/evals 3 7
#
# With no ids, wipes .trial-runs/ and runs every eval in evals.json. With
# explicit ids (e.g. after a partial run died on a session limit), re-runs
# only those, replacing just their own .trial-runs/<id>/ dirs and leaving
# completed trials in place.

set -euo pipefail

unset CDPATH
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"

if [[ $# -lt 1 ]]; then
  echo "usage: run-mcp-trials.sh <skill-evals-dir> [id ...]" >&2
  exit 1
fi

if [[ ! -f "$1/evals.json" ]]; then
  echo "run-mcp-trials: no evals.json in $1" >&2
  exit 1
fi
EVALS_DIR="$(cd "$1" > /dev/null && pwd)"
SKILL_DIR="$(dirname "$EVALS_DIR")"
SKILL_NAME="$(basename "$SKILL_DIR")"
shift

TRIALS_DIR="$EVALS_DIR/.trial-runs"

if [[ $# -gt 0 ]]; then
  IDS="$*"
  for ID in $IDS; do
    rm -rf "${TRIALS_DIR:?}/$ID"
  done
else
  IDS=$(python3 -c "
import json, sys
data = json.load(open(sys.argv[1]))
print(' '.join(str(e['id']) for e in data['evals']))
" "$EVALS_DIR/evals.json")
  rm -rf "$TRIALS_DIR"
fi
mkdir -p "$TRIALS_DIR"

for ID in $IDS; do
  PROMPT=$(python3 -c "
import json, sys
data = json.load(open(sys.argv[1]))
for e in data['evals']:
    if str(e['id']) == sys.argv[2]:
        print(e['prompt'])
        break
else:
    raise SystemExit(f\"no eval with id {sys.argv[2]}\")
" "$EVALS_DIR/evals.json" "$ID")
  RUN_DIR="$TRIALS_DIR/$ID"
  echo "=== Eval $ID ==="

  ENV_FILE="$("$SCRIPT_DIR/run-mcp-eval.sh" "$EVALS_DIR" "$ID" "$RUN_DIR")"
  # shellcheck disable=SC1090
  source "$ENV_FILE"

  # Make the skill under test a project skill of the trial workspace. A
  # trial subprocess only sees skills the machine happens to have installed,
  # so without this a run on a machine where the plugin isn't installed
  # measures the skill's absence and reports it as the skill's behavior.
  # Copying it in makes the trial exercise the working-tree version, which
  # is also what a benchmark of an edited-but-uninstalled skill needs.
  if [[ -f "$SKILL_DIR/SKILL.md" ]]; then
    SKILL_DEST="$WORKSPACE_DIR/.claude/skills/$SKILL_NAME"
    mkdir -p "$SKILL_DEST"
    cp "$SKILL_DIR/SKILL.md" "$SKILL_DEST/"
    for EXTRA in references scripts; do
      [[ -d "$SKILL_DIR/$EXTRA" ]] && cp -R "$SKILL_DIR/$EXTRA" "$SKILL_DEST/"
    done
  else
    echo "  WARNING: no SKILL.md at $SKILL_DIR; the trial will run without the skill"
  fi

  # JSON output mode captures the subprocess's own wall-clock duration and
  # real token usage alongside the reply. `|| true` on the claude call: a
  # failing trial (session limit, transient API error) must not abort the
  # batch under set -e -- its result.json still lands in its own $RUN_DIR
  # and the failure shows up in metrics.json's is_error/parse_error fields.
  # An explicit allowlist rather than --dangerously-skip-permissions: that
  # flag refuses to run as root, which rules out containers and CI, and an
  # allowlist keeps the trial's tool surface auditable. Every stub server is
  # allowed wholesale, including its write tools, so that "the skill wrote
  # nothing" stays a finding about the skill rather than an artifact of the
  # harness blocking the call.
  (
    cd "$WORKSPACE_DIR"
    claude -p --permission-mode acceptEdits \
      --allowedTools "Bash Read Write Edit Glob Grep WebFetch TodoWrite Skill mcp__gmail mcp__trello mcp__atlassian" \
      --strict-mcp-config \
      --mcp-config "$MCP_CONFIG_PATH" --output-format json -- "$PROMPT"
  ) > "$RUN_DIR/result.json" 2> "$RUN_DIR/stderr.txt" || \
    echo "  WARNING: claude exited non-zero for eval $ID; continuing with the next eval"

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
