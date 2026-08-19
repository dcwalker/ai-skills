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
# The nested `claude` subprocess inherits the parent session's credentials,
# so this does run when delegated to an in-session Bash tool call, as well as
# as root, in a container, and in CI -- the allowlist below is what makes the
# last three work. If it fails to authenticate in whatever sandbox you are in,
# run it from a normal logged-in terminal instead. See evals/README.md's "MCP
# stub servers" section for the underlying mechanism.
#
# Usage: bash evals/lib/run-mcp-trials.sh <skill-evals-dir> [id ...]
#
# Set TRIALS_DIR to write the trials somewhere else (see below).
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

# Default output lives beside the evals, gitignored. Override it to put the
# trial workspaces outside the repo: a workspace under evals/ leaves
# evals.json and fixtures/ a few directories up from the trial's own cwd,
# within reach of an executor that goes looking, and that is the answer key.
TRIALS_DIR="${TRIALS_DIR:-$EVALS_DIR/.trial-runs}"

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

  # `|| true` on the claude call: a failing trial (session limit, transient
  # API error) must not abort the batch under set -e -- its events.jsonl
  # still lands in its own $RUN_DIR and the failure shows up in
  # metrics.json's is_error/parse_error fields.
  # An explicit allowlist rather than --dangerously-skip-permissions: that
  # flag refuses to run as root, which rules out containers and CI, and an
  # allowlist keeps the trial's tool surface auditable. Every stub server is
  # allowed wholesale, including its write tools, so that "the skill wrote
  # nothing" stays a finding about the skill rather than an artifact of the
  # harness blocking the call.
  #
  # A private HOME and TMPDIR per trial: a skill that stores anything for
  # the user -- a cache, a profile, a preferences file -- writes it under
  # $HOME, and without this each trial would read what an earlier one left
  # behind. That is both a contaminated trial and a leak between two runs
  # that represent different people. Credentials and config are symlinked
  # back so `claude` still authenticates, and whatever the skill wrote stays
  # under $RUN_DIR/home for the grader to read. A fixture's optional home/
  # directory is copied in first, which is how a trial can start with state
  # already in place (its own, or somebody else's).
  #
  # stream-json keeps the per-event record. The final result event carries
  # the same usage and duration the json format returns, and the assistant
  # events name every tool call -- which is how a grader tells "the skill
  # ran and chose not to search" from "the skill never loaded", two things
  # that look identical in a plain transcript.
  # A trial can still reach the real home directory: HOME is reassigned, but
  # /root (or wherever the account actually lives) stays readable, and a
  # capable model that notices the mismatch will look there. State left by an
  # earlier, non-isolated run is therefore still reachable, which is how a
  # writing trial once rebuilt nothing and reused a style card from a previous
  # session. Warn loudly rather than deleting someone's real data.
  REAL_HOME="$(getent passwd "$(id -un)" | cut -d: -f6)"
  if [[ -n "$REAL_HOME" && -d "$REAL_HOME/writing-style" ]]; then
    echo "  WARNING: $REAL_HOME/writing-style exists and a trial may read it;" \
         "remove it before trusting these results"
  fi

  TRIAL_HOME="$RUN_DIR/home"
  mkdir -p "$RUN_DIR/tmp" "$TRIAL_HOME"
  for CONFIG in .claude .claude.json .config; do
    [[ -e "$HOME/$CONFIG" && ! -e "$TRIAL_HOME/$CONFIG" ]] && \
      ln -s "$HOME/$CONFIG" "$TRIAL_HOME/$CONFIG"
  done
  if [[ -d "$EVALS_DIR/fixtures/$ID/home" ]]; then
    cp -R "$EVALS_DIR/fixtures/$ID/home/." "$TRIAL_HOME/"
  fi

  # run_turn <prompt> [session-id]: one claude turn, events appended to
  # events.jsonl. With a session id it resumes that session, which is what
  # makes a multi-turn eval (draft, then revise, then revise again) a real
  # conversation rather than one prompt describing several.
  run_turn() {
    local turn_prompt="$1" resume_id="${2:-}"
    local -a resume_flag=()
    [[ -n "$resume_id" ]] && resume_flag=(--resume "$resume_id")
    (
      cd "$WORKSPACE_DIR"
      HOME="$TRIAL_HOME" TMPDIR="$RUN_DIR/tmp" \
        claude -p --permission-mode acceptEdits \
        --allowedTools "Bash Read Write Edit Glob Grep WebFetch TodoWrite Skill mcp__gmail mcp__trello mcp__atlassian mcp__slack" \
        --strict-mcp-config --verbose "${resume_flag[@]}" \
        --mcp-config "$MCP_CONFIG_PATH" --output-format stream-json -- "$turn_prompt"
    ) >> "$RUN_DIR/events.jsonl" 2>> "$RUN_DIR/stderr.txt" || \
      echo "  WARNING: claude exited non-zero for eval $ID; continuing"
  }

  : > "$RUN_DIR/events.jsonl"
  : > "$RUN_DIR/stderr.txt"
  run_turn "$PROMPT"

  # A fixture's follow_ups drive later turns of the same session.
  FOLLOW_UPS=$(python3 -c "
import json, sys
data = json.load(open(sys.argv[1]))
for e in data['evals']:
    if str(e['id']) == sys.argv[2]:
        print(len(e.get('follow_ups', [])))
        break
" "$EVALS_DIR/evals.json" "$ID")
  if [[ "$FOLLOW_UPS" -gt 0 ]]; then
    SESSION_ID=$(python3 -c "
import json, sys
for line in open(sys.argv[1]):
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue
    if event.get('type') == 'result' and event.get('session_id'):
        print(event['session_id'])
        break
" "$RUN_DIR/events.jsonl")
    for (( TURN=0; TURN<FOLLOW_UPS; TURN++ )); do
      if [[ -z "$SESSION_ID" ]]; then
        echo "  WARNING: no session id to resume; skipping follow-up turns for eval $ID"
        break
      fi
      NEXT=$(python3 -c "
import json, sys
data = json.load(open(sys.argv[1]))
for e in data['evals']:
    if str(e['id']) == sys.argv[2]:
        print(e['follow_ups'][int(sys.argv[3])])
        break
" "$EVALS_DIR/evals.json" "$ID" "$TURN")
      echo "  follow-up $((TURN + 1))/$FOLLOW_UPS"
      run_turn "$NEXT" "$SESSION_ID"
    done
  fi

  python3 - "$RUN_DIR" <<'PYEOF'
import json, sys
run_dir = sys.argv[1]

# events.jsonl is one JSON object per line, across every turn of the trial:
# each turn ends with a "result" event carrying that turn's usage and
# duration, and each assistant event names the tools it called.
results, tool_calls = [], []
parse_error = "no terminal result event in events.jsonl"
try:
    with open(f"{run_dir}/events.jsonl") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue        # a partial final line on a killed trial
            if event.get("type") == "result":
                results.append(event)
            elif event.get("type") == "assistant":
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use":
                        tool_calls.append({"turn": len(results) + 1,
                                           "name": block.get("name"),
                                           "input": block.get("input")})
except OSError as e:
    parse_error = str(e)

with open(f"{run_dir}/tools.log", "w") as f:
    for call in tool_calls:
        f.write(json.dumps(call) + "\n")

if not results:
    with open(f"{run_dir}/metrics.json", "w") as f:
        json.dump({"parse_error": parse_error, "tool_calls": len(tool_calls),
                   "note": "events.jsonl was missing or held no result event; "
                           "inspect it manually alongside stderr.txt"}, f, indent=2)
    print(f"  WARNING: {parse_error}; wrote placeholder metrics.json and "
          "continuing with the next eval")
    sys.exit(0)

# One transcript for the whole conversation, turns kept separate so a grader
# can see what each revision actually changed.
with open(f"{run_dir}/transcript.txt", "w") as f:
    for turn, result in enumerate(results, start=1):
        if len(results) > 1:
            f.write(f"===== turn {turn} =====\n")
        f.write(result.get("result", ""))
        f.write("\n")


def total(key, source):
    return sum(source(r).get(key) or 0 for r in results)


usage = lambda r: r.get("usage", {})
metrics = {
    "turns_run": len(results),
    "duration_seconds": round(total("duration_ms", lambda r: r) / 1000, 3),
    "duration_api_seconds": round(total("duration_api_ms", lambda r: r) / 1000, 3),
    "num_turns": total("num_turns", lambda r: r),
    "total_cost_usd": total("total_cost_usd", lambda r: r),
    "tool_calls": len(tool_calls),
    "skill_invoked": any(c["name"] == "Skill" for c in tool_calls),
    "tokens": {
        "input": total("input_tokens", usage),
        "output": total("output_tokens", usage),
        "cache_creation_input": total("cache_creation_input_tokens", usage),
        "cache_read_input": total("cache_read_input_tokens", usage),
    },
    "is_error": any(r.get("is_error") for r in results),
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
