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

# Trials require the Bash sandbox (failIfUnavailable, below). Check once,
# before anything is cleared, rather than fail every trial while the batch
# carries on; see the matching check in evals/lib/run-mcp-trials.sh.
PREFLIGHT_LOG="$(mktemp)"
if ! CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --tools Bash --strict-mcp-config \
    --no-session-persistence \
    --settings '{"sandbox":{"enabled":true,"failIfUnavailable":true}}' \
    -- "Reply with OK." < /dev/null > /dev/null 2> "$PREFLIGHT_LOG"; then
  echo "ERROR: Claude Code could not start with its Bash sandbox, which every" >&2
  echo "  trial requires. Its output follows; nothing under TRIALS_DIR was touched." >&2
  cat "$PREFLIGHT_LOG" >&2
  rm -f "$PREFLIGHT_LOG"
  exit 1
fi
rm -f "$PREFLIGHT_LOG"

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
# Resolved once, as evals/lib/run-mcp-trials.sh does: an Edit allow rule must
# match both the path a tool asks for and the file it resolves to.
TRIALS_DIR="$(cd "$TRIALS_DIR" && pwd -P)"

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
  # The non-MCP tools are load-bearing, not filler: Step 2 and Step 7c each
  # define an MCP -> skill -> CLI -> REST hierarchy, and run-mcp-eval.sh
  # deliberately isolates the two shell paths triage/SKILL.md names (curl to
  # Jira's REST API, and gh) by scrubbing credentials and shadowing gh, so
  # those tiers are meant to be exercisable in a trial. Without Bash they can
  # never fire. Every stub server is allowed wholesale, including its write
  # tools, so that "the skill wrote nothing" stays a finding about the skill
  # rather than an artifact of the harness blocking the call. Servers come
  # from this fixture's own mcp-config.json, so a fixture that wires up a new
  # service is covered without editing this list.
  #
  # Write and Edit are not on the list: a bare tool name allows every path,
  # and a trial of another skill wrote into the real home that way (issue
  # #88). Instead the trial runs in dontAsk mode, which denies any call that
  # would otherwise prompt, and TRIAL_SETTINGS below allows file writes under
  # $RUN_DIR only. Bash runs in the sandbox, writable only under $RUN_DIR,
  # with no unsandboxed retry and no fallback if the sandbox cannot start,
  # as in evals/lib/run-mcp-trials.sh. Unlike there, a WebFetch(domain:*)
  # allow rule opens the sandbox's network to every host, so the curl tier
  # above meets the network it always has (the bare WebFetch on the list
  # already allows the tool itself). With --output-format json there is no
  # per-call record, so the shared driver's after-the-fact write check is not
  # repeated here; this driver has no private HOME either, so the sandbox is
  # what keeps a Bash write off the real one. disableAllHooks is not set:
  # with it, the managed-only instruction-files setting below stopped
  # applying and the developer's ~/.claude/rules loaded into the trial.
  # https://code.claude.com/docs/en/sandboxing
  #
  # A read loop rather than `mapfile`, which needs bash 4: macOS ships bash
  # 3.2 as /bin/bash, and the script failed there before running any trial.
  PERM_ARGS=()
  while IFS= read -r line; do
    PERM_ARGS+=("$line")
  done < <(python3 -c "
import json
config = json.load(open('$MCP_CONFIG_PATH'))
print('--allowedTools')
print('Bash Read Glob Grep WebFetch TodoWrite Skill '
      + ' '.join('mcp__' + s for s in config['mcpServers']))
")
  RUN_DIR_REAL="$(cd "$RUN_DIR" && pwd -P)"
  mkdir -p "$RUN_DIR_REAL/tmp"
  TRIAL_SETTINGS="$(python3 -c '
import json, sys
print(json.dumps({
    "pluginConfigs": {"agents-md@builtin": {"options": {"instructionFiles": "managed-only"}}},
    "enabledPlugins": {"life-skills@dcwalker-skills": False},
    "permissions": {"allow": [f"Edit(/{sys.argv[1]}/**)", "WebFetch(domain:*)"]},
    "sandbox": {
        "enabled": True,
        "allowUnsandboxedCommands": False,
        "failIfUnavailable": True,
        "filesystem": {"allowWrite": [sys.argv[1]]},
    },
}))
' "$RUN_DIR_REAL")"

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
  #
  # Keep the running user's own instructions out of the trial. Without this,
  # ~/.claude/rules/, ~/.claude/CLAUDE.md, auto memory, and any AGENTS.md above
  # the workspace load into every trial wherever it runs, and a user rule such
  # as "ask before changing data" made trials refuse the writes they were
  # graded on. The "managed-only" instruction-files setting leaves out user,
  # project, and local CLAUDE.md files, .claude/rules/ files, and every
  # AGENTS.md, but not skills, so the staged triage skill still loads.
  # CLAUDE_CODE_DISABLE_AUTO_MEMORY covers auto memory, which managed-only
  # keeps. Both are documented at https://code.claude.com/docs/en/memory and
  # need Claude Code v2.1.277 or later. Triage fixtures carry no instruction
  # files of their own, so nothing a fixture means to say is lost.
  #
  # The enabledPlugins entry turns off the installed life-skills plugin, whose
  # `life-skills:triage` would otherwise sit beside the staged copy, and a
  # trial that picks it runs the installed release instead of the working
  # tree. See the matching comment in evals/lib/run-mcp-trials.sh.
  (
    cd "$WORKSPACE_DIR"
    CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 CLAUDE_CODE_TMPDIR="$RUN_DIR_REAL/tmp" \
      claude -p --permission-mode dontAsk "${PERM_ARGS[@]}" --strict-mcp-config \
      --settings "$TRIAL_SETTINGS" \
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
