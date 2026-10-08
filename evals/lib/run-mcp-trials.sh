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
# The nested `claude` subprocess inherits the parent session's credentials, so
# this does run when delegated to an in-session Bash tool call. It also runs as
# root, in a container, and in CI -- the allowlist below is what makes those
# three work -- provided Claude Code's Bash sandbox can start there (on Linux
# it needs bubblewrap and socat). A preflight checks that once, before any
# trial runs. If it fails to authenticate in whatever sandbox you are in, run
# it from a normal logged-in terminal instead. See evals/README.md's "MCP stub
# servers" section for the underlying mechanism.
#
# Usage: bash evals/lib/run-mcp-trials.sh <skill-evals-dir> [id ...]
#
# Set TRIALS_DIR to write the trials somewhere else (see below). Set
# SIMULATED_USER=1 to have a model play the user in evals that carry no
# follow_ups (see "simulated user" below); SIMULATED_USER_MAX_TURNS caps the
# replies it sends (default 40).
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

# The trial's staged copy of the skill (below) is not the only one it can
# see: the symlinked plugins directory carries the installed release too,
# as `<plugin>:<skill>`. A trial that picks the installed copy runs stale
# instructions, and nothing in its transcript says so. Turning the skill's
# own plugin off for the trial leaves the staged copy as the only one. The
# other skills in that plugin go with it; no MCP-backed eval relies on a
# sibling skill today. Hiding just the one skill is not possible: the
# skillOverrides setting does not apply to plugin skills. The per-trial
# TRIAL_SETTINGS below carries this enabledPlugins entry.
PLUGIN_NAME="$(basename "$(dirname "$(dirname "$SKILL_DIR")")")"
MARKETPLACE_FILE="$SCRIPT_DIR/../../.claude-plugin/marketplace.json"
MARKETPLACE_NAME="$(python3 -c "import json, sys; print(json.load(open(sys.argv[1]))['name'])" \
  "$MARKETPLACE_FILE")"

# Default output lives beside the evals, gitignored. Override it to put the
# trial workspaces outside the repo: a workspace under evals/ leaves
# evals.json and fixtures/ a few directories up from the trial's own cwd,
# within reach of an executor that goes looking, and that is the answer key.
TRIALS_DIR="${TRIALS_DIR:-$EVALS_DIR/.trial-runs}"

# A trial can always reach the real home directory: HOME is reassigned, but the
# account's actual home stays readable, and its own working directory is inside
# it. Writes there are now refused (see the permission rules and sandbox set up
# per trial below), and caught afterwards if one gets through; this check for
# the writing skill's style cache predates both and stays as a backstop. It
# needs to know the directory was absent beforehand.
#
# `getent` is glibc-only; macOS keeps the same record in Directory Services.
# Either lookup may fail on an unusual account, and an empty result is fine:
# the checks below then simply do not fire.
if command -v getent > /dev/null 2>&1; then
  REAL_HOME="$(getent passwd "$(id -un)" | cut -d: -f6)" || REAL_HOME=""
else
  REAL_HOME="$(dscl . -read "/Users/$(id -un)" NFSHomeDirectory 2> /dev/null \
    | awk '{ print $2 }')" || REAL_HOME=""
fi

# Refuse to start if a real style cache is already there. Warning and carrying
# on is not enough: the post-trial check cannot tell "this trial wrote here"
# from "this was already here", so it would quarantine a developer's own cache
# as though a trial had created it -- and a later full run does
# `rm -rf "$TRIALS_DIR"`, taking the quarantined copy with it. Stopping here
# keeps the decision about someone's own data with them.
if [[ -n "$REAL_HOME" && -e "$REAL_HOME/writing-style" ]]; then
  echo "ERROR: $REAL_HOME/writing-style already exists." >&2
  echo "  Trials cannot run while it is there. The escape check could not tell" >&2
  echo "  your own cache apart from one a trial created, and would move it aside." >&2
  echo "  Move or delete it yourself, then re-run. This script will not touch it." >&2
  exit 1
fi

# What `claude -p` prints when it has no usable login. The preflight and every
# trial turn check for it, because a trial that cannot log in exits at once
# with zero tokens, and a batch that carried on would report thirty of them as
# ordinary results.
AUTH_FAILURE_PATTERN='Not logged in|Failed to authenticate|Please run /login'

# Trials require the Bash sandbox (failIfUnavailable, below), and Claude Code
# exits at startup when it cannot start one. Bash is the one tool offered, so
# the sandbox has something to start for; the prompt never needs it. Without this check, every trial
# would fail the same way while the batch reported each as an ordinary
# non-zero exit and carried on, finishing with nothing measured. It runs
# before anything under TRIALS_DIR is cleared, so a machine that cannot run
# trials does not lose the last run's results finding out.
#
# Its stdout is kept as well as its stderr: `claude -p` prints a login failure
# ("Not logged in", "Failed to authenticate") on stdout, so discarding stdout
# reported an expired login as a sandbox failure, with no output to show why.
PREFLIGHT_LOG="$(mktemp)"
if ! CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 claude -p --tools Bash --strict-mcp-config \
    --no-session-persistence \
    --settings '{"sandbox":{"enabled":true,"failIfUnavailable":true}}' \
    -- "Reply with OK." < /dev/null > "$PREFLIGHT_LOG" 2>&1; then
  if grep -qE "$AUTH_FAILURE_PATTERN" "$PREFLIGHT_LOG"; then
    echo "ERROR: claude is not logged in, so no trial can run. Its output follows;" >&2
    echo "  nothing under TRIALS_DIR was touched. Log in (claude auth login) and re-run." >&2
  else
    echo "ERROR: Claude Code could not start with its Bash sandbox, which every" >&2
    echo "  trial requires. Its output follows; nothing under TRIALS_DIR was touched." >&2
    echo "  See https://code.claude.com/docs/en/sandboxing for its requirements." >&2
  fi
  cat "$PREFLIGHT_LOG" >&2
  rm -f "$PREFLIGHT_LOG"
  exit 1
fi
rm -f "$PREFLIGHT_LOG"

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
# Every path below derives from the resolved trials directory. A permission
# rule only matches when the path a tool asks for and the file it resolves to
# both fall under it, so a run dir reached through a symlink (/tmp on macOS)
# would name a private HOME no rule covers.
TRIALS_DIR="$(cd "$TRIALS_DIR" && pwd -P)"

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

  # Writes stay inside $RUN_DIR, which holds the workspace, the private HOME,
  # and TMPDIR. A private HOME alone does not do it: eval 19 of the
  # organize-meeting-notes benchmark for issue #82 wrote journal.md into the
  # real home by absolute path. Two documented mechanisms close the two ways a
  # trial writes files, and each needs the resolved path (/tmp is a symlink
  # on macOS, and a rule must name the path the tool will see):
  #
  # - The Write and Edit tools: Claude Code checks file writes against
  #   `Edit(path)` rules, and a bare `Write` or `Edit` in --allowedTools
  #   allows every path, which is how journal.md got through. So the trial
  #   runs in dontAsk mode, which denies any call that would otherwise
  #   prompt, with one allow rule for $RUN_DIR (`//` marks an absolute path).
  #   https://code.claude.com/docs/en/permissions
  # - Bash: permission rules match the command text Claude writes, not what
  #   the program then does, so Bash writes are contained by the OS-level
  #   sandbox instead, writable only under $RUN_DIR, with no unsandboxed
  #   retry and no fallback to running unsandboxed if the sandbox cannot
  #   start. Its network allowlist holds only what WebFetch(domain:...)
  #   allow rules add; the trial adds none, so Bash reaches only hosts such
  #   a rule in project settings names (see evals/README.md), and every
  #   service a trial talks to here is a stub. Hooks from the developer's
  #   enabled plugins still run, outside the sandbox: disableAllHooks would
  #   stop them, but it also stopped the managed-only instruction-files
  #   setting triage's driver relies on (issue #88), so it is not used.
  #   https://code.claude.com/docs/en/sandboxing
  RUN_DIR_REAL="$(cd "$RUN_DIR" && pwd -P)"
  TRIAL_SETTINGS="$(python3 -c '
import json, sys
plugin, run_dir = sys.argv[1], sys.argv[2]
print(json.dumps({
    "enabledPlugins": {plugin: False},
    "permissions": {"allow": [f"Edit(/{run_dir}/**)"]},
    "sandbox": {
        "enabled": True,
        "allowUnsandboxedCommands": False,
        "failIfUnavailable": True,
        "filesystem": {"allowWrite": [run_dir]},
    },
}))
' "$PLUGIN_NAME@$MARKETPLACE_NAME" "$RUN_DIR_REAL")"

  # `|| true` on the claude call: a failing trial (session limit, transient
  # API error) must not abort the batch under set -e -- its events.jsonl
  # still lands in its own $RUN_DIR and the failure shows up in
  # metrics.json's is_error/parse_error fields.
  # The built-in tools a trial has at all. --allowedTools only pre-approves
  # calls; a tool that needs no approval runs whether or not it is listed, and
  # trials did call the host's Artifact and Agent tools until this set was
  # named. Write and Edit are here because the Edit rule in TRIAL_SETTINGS
  # confines them to the run directory; ToolSearch loads the stub servers'
  # deferred tools. MCP tools come from --mcp-config, not from this list.
  #
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
  TRIAL_HOME="$RUN_DIR/home"
  mkdir -p "$RUN_DIR/tmp" "$TRIAL_HOME"
  # $HOME is reassigned, but a trial can still write to the real home if it
  # learns the path -- and it does not have to snoop to learn it. Symlinks in
  # $TRIAL_HOME name their targets, and .claude.json carries a `projects` map
  # keyed by absolute paths. That is not hypothetical: a full 27-trial run
  # wrote 14 style cards into the developer's real ~/writing-style, and later
  # trials then read cards earlier trials had left there, which is precisely
  # the cross-trial contamination this isolation exists to prevent.
  #
  # So: .config is symlinked (gh and git config, needed by other skills'
  # evals), .claude becomes a real directory holding only what a trial needs,
  # and .claude.json is copied with every identity- and path-bearing key
  # removed. Authentication comes from CLAUDE_CODE_OAUTH_TOKEN or the
  # keychain, never from these files.
  [[ -e "$HOME/.config" && ! -e "$TRIAL_HOME/.config" ]] && \
    ln -s "$HOME/.config" "$TRIAL_HOME/.config"

  if [[ -d "$HOME/.claude" && ! -e "$TRIAL_HOME/.claude" ]]; then
    mkdir -p "$TRIAL_HOME/.claude"
    # Copied without permissions, sandbox, or hooks: permission and sandbox
    # arrays merge across settings scopes, so a developer's own allow rules
    # or extra writable paths would widen the boundary set up per trial
    # below, and their hooks run outside it altogether. A file that is not
    # strict JSON is left out with a warning rather than ending the batch.
    for SETTING in settings.json settings.local.json; do
      [[ -f "$HOME/.claude/$SETTING" ]] && { python3 -c '
import json, sys
with open(sys.argv[1]) as fh:
    settings = json.load(fh)
for key in ("permissions", "sandbox", "hooks"):
    settings.pop(key, None)
with open(sys.argv[2], "w") as fh:
    json.dump(settings, fh)
' "$HOME/.claude/$SETTING" "$TRIAL_HOME/.claude/$SETTING" 2> /dev/null || \
        echo "  WARNING: could not read ~/.claude/$SETTING as JSON; the trial runs without it"; }
    done
    # Plugins are 22M and read-only to a trial, so they stay a symlink rather
    # than being copied 27 times. The rest of ~/.claude -- projects/, sessions/,
    # history.jsonl, 268M of transcripts naming the real user -- is left out.
    [[ -d "$HOME/.claude/plugins" ]] && \
      ln -s "$HOME/.claude/plugins" "$TRIAL_HOME/.claude/plugins"
  fi

  if [[ -f "$HOME/.claude.json" && ! -e "$TRIAL_HOME/.claude.json" ]]; then
    python3 -c '
import json, sys
with open(sys.argv[1]) as fh:
    config = json.load(fh)
# Identity: Claude Code injects oauthAccount into its own system prompt, which
# told trials whose machine they were on and made them refuse the fixture
# persona. Paths: every one of these names the real home directory.
for key in ("oauthAccount", "userID", "anonymousId", "machineID",
            "projects", "githubRepoPaths", "appleTerminalBackupPath"):
    config.pop(key, None)
with open(sys.argv[2], "w") as fh:
    json.dump(config, fh)
' "$HOME/.claude.json" "$TRIAL_HOME/.claude.json" || {
      echo "  WARNING: could not sanitise .claude.json; trial may reach the real home" >&2
    }
  fi

  if [[ -d "$EVALS_DIR/fixtures/$ID/home" ]]; then
    cp -R "$EVALS_DIR/fixtures/$ID/home/." "$TRIAL_HOME/"
  fi

  # run_turn <prompt> [session-id]: one claude turn, events appended to
  # events.jsonl. With a session id it resumes that session, which is what
  # makes a multi-turn eval (draft, then revise, then revise again) a real
  # conversation rather than one prompt describing several.
  TRIAL_TOOLS="Bash,Read,Glob,Grep,Write,Edit,WebFetch,Skill,ToolSearch"
  run_turn() {
    local turn_prompt="$1" resume_id="${2:-}"
    local -a resume_flag=()
    [[ -n "$resume_id" ]] && resume_flag=(--resume "$resume_id")
    (
      cd "$WORKSPACE_DIR"
      HOME="$TRIAL_HOME" TMPDIR="$RUN_DIR/tmp" CLAUDE_CODE_TMPDIR="$RUN_DIR/tmp" \
        claude -p --permission-mode dontAsk \
        --tools "$TRIAL_TOOLS" \
        --allowedTools "Bash Read Glob Grep WebFetch TodoWrite Skill mcp__gmail mcp__trello mcp__atlassian mcp__slack mcp__calendar" \
        --strict-mcp-config --verbose ${resume_flag[@]+"${resume_flag[@]}"} \
        --settings "$TRIAL_SETTINGS" \
        --mcp-config "$MCP_CONFIG_PATH" --output-format stream-json -- "$turn_prompt" \
        < /dev/null
    ) >> "$RUN_DIR/events.jsonl" 2>> "$RUN_DIR/stderr.txt" || {
      # The preflight runs with the real HOME; a trial runs with its own, so a
      # login the preflight could use can still be out of a trial's reach.
      # Only the turn's last event and stderr are checked: a skill's own reply
      # may mention a login, and that must not stop a batch.
      if { tail -n 1 "$RUN_DIR/events.jsonl"; cat "$RUN_DIR/stderr.txt"; } \
          | grep -qE "$AUTH_FAILURE_PATTERN"; then
        echo "ERROR: eval $ID could not log in under its private HOME; stopping the batch." >&2
        echo "  Nothing after it was run. See $RUN_DIR/events.jsonl." >&2
        exit 1
      fi
      echo "  WARNING: claude exited non-zero for eval $ID; continuing"
    }
  }

  : > "$RUN_DIR/events.jsonl"
  TRIAL_START="$(date +%s)"
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
  if [[ "$FOLLOW_UPS" -gt 0 ]]; then
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
  elif [[ "${SIMULATED_USER:-}" == "1" ]]; then
    # Simulated user: an eval whose skill interviews the user cannot be
    # scripted in advance, because canned replies arrive in a fixed order
    # whatever the skill asks. Instead a second `claude -p` plays the user,
    # one reply per turn, from the eval's prompt and the conversation so far.
    # It never sees expected_output or expectations, which are the answer
    # key, and it runs with no tools, no MCP servers, and none of the
    # running user's instructions, in its own empty directory. It replies
    # DONE once the skill has delivered its result and asks nothing more.
    # conversation.txt records both sides for the grader; transcript.txt
    # holds only the skill's turns.
    SIM_DIR="$RUN_DIR/simulated-user"
    mkdir -p "$SIM_DIR"
    SIM_SYSTEM="You are role-playing the user in a test conversation with an AI assistant. The conversation so far follows, starting with your own opening message. Write only your next message to the assistant, in the first person, as that user. Stay consistent with your opening message: never contradict it, and follow any instruction it gives about how you will answer (for example, declining an offer you said you would decline). Answer what the assistant asks; when it asks something your opening message does not cover, give a short, plausible answer that fits it. Do not invent notes, files, or pasted material your opening message does not say you have. Approve the assistant's proposals and drafts unless your opening message says otherwise. Keep replies brief. If the assistant has delivered its final result and asks you nothing more, reply with exactly: DONE"
    printf 'USER:\n%s\n\n' "$PROMPT" > "$RUN_DIR/conversation.txt"
    SIM_TURNS=0
    while (( SIM_TURNS < ${SIMULATED_USER_MAX_TURNS:-40} )); do
      if [[ -z "$SESSION_ID" ]]; then
        echo "  WARNING: no session id to resume; stopping the simulated user for eval $ID"
        break
      fi
      python3 -c "
import json, sys
last = ''
for line in open(sys.argv[1]):
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue
    if event.get('type') == 'result':
        last = event.get('result', '')
print('ASSISTANT:')
print(last)
print()
" "$RUN_DIR/events.jsonl" >> "$RUN_DIR/conversation.txt"
      REPLY=$(cd "$SIM_DIR" && HOME="$TRIAL_HOME" TMPDIR="$RUN_DIR/tmp" \
        CLAUDE_CODE_TMPDIR="$RUN_DIR/tmp" \
        CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 \
        claude -p --tools "" --strict-mcp-config --no-session-persistence \
        --settings '{"pluginConfigs":{"agents-md@builtin":{"options":{"instructionFiles":"managed-only"}}}}' \
        --system-prompt "$SIM_SYSTEM" --output-format text \
        -- "$(cat "$RUN_DIR/conversation.txt")" < /dev/null 2>> "$RUN_DIR/stderr.txt") || REPLY=""
      if [[ -z "$REPLY" ]]; then
        echo "  WARNING: the simulated user returned nothing; stopping eval $ID here"
        break
      fi
      [[ "$(echo "$REPLY" | tr -d '[:space:]')" == "DONE" ]] && break
      printf 'USER:\n%s\n\n' "$REPLY" >> "$RUN_DIR/conversation.txt"
      SIM_TURNS=$((SIM_TURNS + 1))
      echo "  simulated user reply $SIM_TURNS"
      run_turn "$REPLY" "$SESSION_ID"
    done
    echo "$SIM_TURNS" > "$RUN_DIR/simulated-user-turns"
    if (( SIM_TURNS >= ${SIMULATED_USER_MAX_TURNS:-40} )); then
      echo "  WARNING: eval $ID reached the simulated-user turn cap before finishing"
    fi
  fi

  python3 - "$RUN_DIR" "$SKILL_NAME" "$RUN_DIR_REAL" "$WORKSPACE_DIR" "$TRIAL_HOME" \
    "$TRIAL_START" <<'PYEOF'
import json, os, re, shlex, sys
run_dir, skill_name, run_dir_real, workspace, trial_home = sys.argv[1:6]
trial_start = float(sys.argv[6]) - 1     # a second's slack for clock granularity

# events.jsonl is one JSON object per line, across every turn of the trial:
# each turn ends with a "result" event carrying that turn's usage and
# duration, and each assistant event names the tools it called.
results, tool_calls, tool_results = [], [], {}
parse_error = "no terminal result event in events.jsonl"


def blocks(event):
    content = (event.get("message") or {}).get("content")
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


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
            if not isinstance(event, dict):
                continue
            if event.get("type") == "result":
                results.append(event)
            elif event.get("type") == "assistant":
                for block in blocks(event):
                    if block.get("type") == "tool_use":
                        tool_calls.append({"turn": len(results) + 1,
                                           "id": block.get("id"),
                                           "name": block.get("name"),
                                           "input": block.get("input")})
            elif event.get("type") == "user":
                for block in blocks(event):
                    if block.get("type") == "tool_result":
                        text = block.get("content")
                        tool_results[block.get("tool_use_id")] = (
                            bool(block.get("is_error")),
                            text if isinstance(text, str) else json.dumps(text))
except OSError as e:
    parse_error = str(e)

with open(f"{run_dir}/tools.log", "w") as f:
    for call in tool_calls:
        f.write(json.dumps({k: v for k, v in call.items() if k != "id"}) + "\n")


# Writes aimed outside $RUN_DIR. The permission rules and sandbox set up above
# should refuse every one, so each is sorted by what became of it:
#   confirmed    the target was created after the trial started (where the
#                filesystem records creation, as macOS does), or changed after
#                it started without the sandbox or permission system refusing
#                the call. A compound command can fail in one part after
#                writing in another, so a tool error alone, without a refusal
#                message, does not clear a write. A directory's own
#                timestamps move whenever anything writes inside it, so they
#                never confirm; a copy into one is judged by the file it would
#                have put there;
#   refused      otherwise, when the tool reported an error, or the sandbox's
#                or permission system's refusal appears in its output;
#   unconfirmed  otherwise: a deletion, which leaves nothing to look at, or a
#                command that touched nothing (mkdir -p of a directory that
#                already existed).
# Only a confirmed write stops the run; the other two are counted and warned
# about, since a refused save still explains why a skill's output went
# missing. File tools are checked exactly. Bash is checked by its write
# targets: redirections, and the operands of commands that create, edit,
# move, or delete files, read through a shell tokenizer so quoted text and
# heredoc bodies are not taken for commands. That catches the common forms,
# not every way a shell can write (an interpreter's own file calls, a path
# built in a variable); the sandbox is what actually contains Bash. Relative
# and ~ paths resolve inside the workspace and private HOME.
def resolve(path):
    if path == "~" or path.startswith("~/"):
        path = trial_home + path[1:]
    path = os.path.join(workspace, os.path.expanduser(path))
    # The deepest existing ancestor carries any symlinks, such as /tmp on
    # macOS; the rest of the path did not exist to resolve, or was removed.
    head, tail = path, []
    while head and not os.path.exists(head):
        head, part = os.path.split(head)
        tail.insert(0, part)
    return os.path.join(os.path.realpath(head or "/"), *tail)


def outside(path):
    real = resolve(path)
    return not (real == run_dir_real or real.startswith(run_dir_real + os.sep)) \
        and not real.startswith("/dev/")


def written(real, blocked):
    try:
        info = os.lstat(real)
    except OSError:
        return False
    born = getattr(info, "st_birthtime", None)
    if born is not None and born >= trial_start:
        return True
    if os.path.isdir(real) and not os.path.islink(real):
        return False
    return not blocked and max(info.st_mtime, info.st_ctime) >= trial_start


# Every operand is written to (mv removes its sources too); for the copy
# family only the last operand is, unless -t names the directory; dd writes
# only to of=, and sed -i or perl -i edit the files after their script.
WRITES_EVERY_ARG = {"tee", "touch", "mkdir", "rm", "rmdir", "mv", "truncate"}
WRITES_LAST_ARG = {"cp", "ln", "install", "rsync", "mv"}
DELETES = {"rm", "rmdir", "mv"}
IN_PLACE = {"sed", "perl"}
# Words that can stand before the command itself: wrappers, assignments, and
# the shell keywords a loop or conditional puts at the start of a segment.
PREFIXES = {"sudo", "env", "command", "nohup", "time", "xargs", "exec", "timeout",
            "nice", "stdbuf", "if", "while", "until", "do", "then", "else",
            "elif", "!", "{", "}"}
# Downloaders name their output file with a flag rather than an operand.
OUTPUT_FLAGS = {"curl": ("-o", "--output"), "wget": ("-O", "--output-document")}
# Redirections that duplicate a file descriptor (2>&1) take a number, not a
# path, unless the shell form writes both streams to a file (>& file).
DUPLICATES = {">&", "<&"}
SEPARATORS = {";", "&&", "||", "|", "&", "|&", "(", ")"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>"}
REFUSAL = re.compile(r"operation not permitted|read-only file system|"
                     r"permission to use \w+ has been denied", re.I)
HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([^\s'\"<>;|&()]+)\1")


def strip_heredocs(command):
    """Drop heredoc bodies: their lines are input, not commands. A `<<` counts
    only when its delimiter line really follows, so `<<` inside quoted text
    or a herestring (`<<<`) leaves the rest of the command alone."""
    lines, out, i = command.split("\n"), [], 0
    while i < len(lines):
        out.append(lines[i])
        match = HEREDOC.search(lines[i])
        if match:
            delimiter = match.group(2)
            end = next((j for j in range(i + 1, len(lines))
                        if lines[j].strip() == delimiter), None)
            if end is not None:
                i = end
        i += 1
    return "\n".join(out)


def bash_targets(command):
    """[(path, is_deletion, sources)] for each absolute or ~ write target;
    sources are what the copy family copies, for a target that is a
    directory."""
    text = strip_heredocs(command).replace("\\\n", " ").replace("\n", " ; ")
    lexer = shlex.shlex(text, posix=True, punctuation_chars=";&|()<>")
    lexer.whitespace_split = True
    lexer.commenters = ""   # `#` mid-word (a URL fragment, $#) is not a comment
    try:
        tokens = list(lexer)
    except ValueError:      # an unbalanced quote: fall back to plain words
        tokens = text.split()
    targets, words = [], []

    def flush():
        while words and (words[0] in PREFIXES or re.match(r"^\w+=", words[0])):
            words.pop(0)
            # a wrapper's own options and numbers (timeout 10, nice -n 5)
            while words and (words[0].startswith("-") or words[0].isdigit()):
                words.pop(0)
        if words:
            name = os.path.basename(words[0])
            operands = [w for w in words[1:] if not w.startswith("-")]
            target_dir = next((words[k + 1] for k, w in enumerate(words[:-1]) if w == "-t"),
                              None) or next((w.split("=", 1)[1] for w in words
                                             if w.startswith("--target-directory=")), None)
            if name in WRITES_LAST_ARG and target_dir:
                targets.append((target_dir, False, [w for w in operands if w != target_dir]))
            elif name in WRITES_LAST_ARG and operands:
                targets.append((operands[-1], False, operands[:-1]))
            if name in WRITES_EVERY_ARG:
                targets.extend((w, name in DELETES, []) for w in operands
                               if not (name == "mv" and (w == operands[-1] or w == target_dir)))
            elif name == "dd":
                targets.extend((w[3:], False, []) for w in words[1:] if w.startswith("of="))
            elif name in IN_PLACE and any(w.startswith("-i") or w == "--in-place"
                                          for w in words[1:]):
                targets.extend((w, False, []) for w in operands[1:])
            elif name in OUTPUT_FLAGS:
                short, long = OUTPUT_FLAGS[name]
                for k, w in enumerate(words[1:-1], start=1):
                    if w in (short, long):
                        targets.append((words[k + 1], False, []))
                targets.extend((w.split("=", 1)[1], False, []) for w in words
                               if w.startswith(long + "="))
        words.clear()

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in REDIRECTS and i + 1 < len(tokens):
            targets.append((tokens[i + 1], False, []))
            i += 2
            continue
        if token in DUPLICATES and i + 1 < len(tokens):
            if token == ">&" and tokens[i + 1] != "-" and not tokens[i + 1].isdigit():
                targets.append((tokens[i + 1], False, []))
            i += 2
            continue
        if token in SEPARATORS or (token and set(token) <= set(";&|()<>")):
            flush()
        elif token.startswith("#"):
            while i + 1 < len(tokens) and tokens[i + 1] not in SEPARATORS:
                i += 1      # a comment runs to the end of its line
        elif not token.isdigit() or i + 1 >= len(tokens) \
                or tokens[i + 1] not in REDIRECTS | DUPLICATES:
            words.append(token)     # an fd number before > or >& is not a word
        i += 1
    flush()
    return [(t, d, src) for t, d, src in targets if t.startswith(("/", "~"))]


# Files the harness and its stubs write in the run directory's root. A trial
# writing one directly (eval 6 once emptied trello-calls.log to hide a test
# card) corrupts the evidence graders read, so any such write is recorded in
# tampering.log and counted in metrics.json, whether or not it went through.
HARNESS_FILE = re.compile(r"(-calls\.log|-state-out\.json|-state-seed\.json|\.counts\.json)$|"
                          r"^(tools\.log|events\.jsonl|metrics\.json|escapes\.log|"
                          r"tampering\.log|env\.sh|mcp-config\.json|eval\.json)$")
tampering = []

escapes, detection_error = [], None
try:
    for call in tool_calls:
        params = call.get("input") if isinstance(call.get("input"), dict) else {}
        if call["name"] in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
            paths = [(params.get("file_path") or params.get("notebook_path") or "", False, [])]
        elif call["name"] == "Bash" and isinstance(params.get("command"), str):
            paths = bash_targets(params["command"])
        else:
            continue
        is_error, text = tool_results.get(call["id"], (False, ""))
        # A refusal message is evidence the boundary held; a bare tool error
        # is not, since a later part of the same command may be what failed.
        blocked = bool(REFUSAL.search(text or ""))
        for path, deletion, sources in paths:
            if path and os.path.dirname(resolve(path)) == run_dir_real \
                    and HARNESS_FILE.search(os.path.basename(resolve(path))):
                tampering.append({"turn": call["turn"], "tool": call["name"], "path": path,
                                  "status": "refused" if is_error or blocked else "attempted"})
                continue
            if not path or not outside(path):
                continue
            real = resolve(path)
            candidates = [real]
            if sources and os.path.isdir(real) and not os.path.islink(real):
                candidates = [os.path.join(real, os.path.basename(src.rstrip("/")))
                              for src in sources]
            if not deletion and any(written(c, blocked) for c in candidates):
                status = "confirmed"
            elif is_error or blocked:
                status = "refused"
            else:
                status = "unconfirmed"
            escapes.append({"turn": call["turn"], "tool": call["name"], "path": path,
                            "resolved": real, "status": status})
except Exception as e:      # a detection bug must not abort the batch
    detection_error = f"{type(e).__name__}: {e}"
    print(f"  WARNING: the outside-write check failed ({detection_error}); "
          "inspect tools.log by hand")

if escapes:
    with open(f"{run_dir}/escapes.log", "w") as f:
        for escape in escapes:
            f.write(json.dumps(escape) + "\n")
if tampering:
    with open(f"{run_dir}/tampering.log", "w") as f:
        for entry in tampering:
            f.write(json.dumps(entry) + "\n")
    print(f"  WARNING: {len(tampering)} write(s) aimed at harness files in the run "
          "directory (call logs, stub state, metrics); see tampering.log. Grade "
          "this trial from events.jsonl, not its call logs.")
count = {status: sum(e["status"] == status for e in escapes)
         for status in ("confirmed", "unconfirmed", "refused")}
outside_writes = {"writes_outside_run_dir": count["confirmed"],
                  "writes_outside_run_dir_unconfirmed": count["unconfirmed"],
                  "writes_outside_run_dir_refused": count["refused"],
                  "harness_file_writes": len(tampering),
                  "outside_write_check_error": detection_error}
if count["refused"] or count["unconfirmed"]:
    print(f"  WARNING: {count['refused']} refused and {count['unconfirmed']} unconfirmed "
          "write(s) aimed outside the run directory; see escapes.log")

if not results:
    with open(f"{run_dir}/metrics.json", "w") as f:
        json.dump({"parse_error": parse_error, "tool_calls": len(tool_calls),
                   **outside_writes,
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
installed_calls = [c["input"].get("skill") for c in tool_calls
                   if c["name"] == "Skill"
                   and str((c.get("input") or {}).get("skill", "")).endswith(":" + skill_name)]
metrics = {
    "turns_run": len(results),
    "duration_seconds": round(total("duration_ms", lambda r: r) / 1000, 3),
    "duration_api_seconds": round(total("duration_api_ms", lambda r: r) / 1000, 3),
    "num_turns": total("num_turns", lambda r: r),
    "total_cost_usd": total("total_cost_usd", lambda r: r),
    "tool_calls": len(tool_calls),
    "skill_invoked": any(c["name"] == "Skill" for c in tool_calls),
    # The staged copy is invoked by its bare name; a plugin-qualified name
    # (`life-skills:organize-meeting-notes`) means the installed release ran.
    "installed_skill_invoked": installed_calls,
    "tokens": {
        "input": total("input_tokens", usage),
        "output": total("output_tokens", usage),
        "cache_creation_input": total("cache_creation_input_tokens", usage),
        "cache_read_input": total("cache_read_input_tokens", usage),
    },
    "is_error": any(r.get("is_error") for r in results),
    **outside_writes,
}
with open(f"{run_dir}/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
print(f"  duration: {metrics['duration_seconds']}s, "
      f"tokens in/out: {metrics['tokens']['input']}/{metrics['tokens']['output']}, "
      f"cache read: {metrics['tokens']['cache_read_input']}")
if installed_calls:
    print(f"  WARNING: the trial invoked {installed_calls[0]}, the installed copy, "
          "not the staged one; this trial measured stale instructions")
PYEOF

  # The run refused to start unless $REAL_HOME/writing-style was absent, so
  # anything here now was written by this trial. That is what makes the move
  # below safe: it can only ever be trial output, never someone's own cache.
  #
  # Stopping is the point. A run that continues past an escape silently mixes
  # one trial's cards into every later trial's evidence, and the resulting
  # numbers look ordinary. Failing here means any run that reaches the end is
  # known clean.
  if [[ -n "$REAL_HOME" && -d "$REAL_HOME/writing-style" ]]; then
    ESCAPE_QUARANTINE="$TRIALS_DIR/escaped-home-$ID"
    rm -rf "$ESCAPE_QUARANTINE"
    mv "$REAL_HOME/writing-style" "$ESCAPE_QUARANTINE"
    echo >&2
    echo "  ERROR: eval $ID wrote to $REAL_HOME/writing-style, escaping its" >&2
    echo "  isolated HOME. Moved to $ESCAPE_QUARANTINE for inspection." >&2
    echo "  Stopping: every later trial would have read what it left there," >&2
    echo "  and the run's results would look normal while being contaminated." >&2
    exit 1
  fi

  # Any other write that landed outside $RUN_DIR, found from the trial's own
  # tool calls above. A confirmed one stops the run for the same reason: the
  # trial wrote somewhere real, and what it wrote stays there until someone
  # looks. Refused and unconfirmed attempts were already warned about.
  CONFIRMED_ESCAPES=""
  if [[ -s "$RUN_DIR/escapes.log" ]]; then
    CONFIRMED_ESCAPES="$(python3 -c '
import json, sys
for line in open(sys.argv[1]):
    escape = json.loads(line)
    if escape["status"] == "confirmed":
        print("    turn {turn}, {tool}: {resolved}".format(**escape))
' "$RUN_DIR/escapes.log")"
  fi
  if [[ -n "$CONFIRMED_ESCAPES" ]]; then
    echo >&2
    echo "  ERROR: eval $ID wrote outside its run directory ($RUN_DIR_REAL):" >&2
    echo "$CONFIRMED_ESCAPES" >&2
    echo "  Nothing was moved or deleted. Inspect those paths, then see" >&2
    echo "  $RUN_DIR/escapes.log and tools.log. Stopping the run." >&2
    exit 1
  fi

  echo "  -> saved to $RUN_DIR"
  echo
done

echo "All trials complete. Review $TRIALS_DIR/<id>/: transcript.txt, metrics.json,"
echo "and the per-service <service>-state-out.json / <service>-calls.log files."
