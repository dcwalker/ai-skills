#!/usr/bin/env bash
# Runs triage's MCP-backed eval trials through the shared driver,
# evals/lib/run-mcp-trials.sh, which does all the work: stub servers, the
# staged skill and references/, multi-turn follow_ups, the simulated user,
# the fake GitHub, a private HOME and TMPDIR, and the write checks. See
# evals/README.md's "MCP stub servers" section.
#
# Triage presents one item per reply, so every eval is a conversation: it
# either scripts the user's replies in `follow_ups` or is played by the
# simulated user. Run the suite with SIMULATED_USER=1. Evals with a
# follow_ups key, an empty one included, are never given the simulated user.
#
# The running user's own instructions stay out of every trial: triage's
# evals.json sets "instruction_files": "managed-only", which the driver turns
# into the managed-only instruction-files setting, and the driver sets
# CLAUDE_CODE_DISABLE_AUTO_MEMORY=1. Without them a rule such as "ask before
# changing data" made trials refuse the writes they were graded on.
#
# Usage, from the repo root:
#   TRIALS_DIR="$TMPDIR/triage-trials" SIMULATED_USER=1 \
#     bash plugins/life-skills/skills/triage/evals/run-trials.sh [id ...]
#
# Point TRIALS_DIR under $TMPDIR: a workspace inside this repository or the
# home directory has AGENTS.md files above it, and evals.json and fixtures/
# within reach.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." > /dev/null && pwd)"

exec bash "$REPO_ROOT/evals/lib/run-mcp-trials.sh" "$SCRIPT_DIR" "$@"
