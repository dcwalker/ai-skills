#!/usr/bin/env bash
# Runs create-task's eval trials through the shared driver,
# evals/lib/run-mcp-trials.sh: stub servers for the Trello evals, an empty
# workspace for the conversation_only ones, a private HOME and TMPDIR, and
# the write checks. See evals/README.md's "MCP stub servers" section.
#
# Every eval is single-turn (an empty follow_ups list), so no simulated user
# is needed. The running user's own instructions stay out of every trial:
# evals.json sets "instruction_files": "managed-only".
#
# Usage, from the repo root:
#   TRIALS_DIR="$TMPDIR/create-task-trials" \
#     bash plugins/life-skills/skills/create-task/evals/run-trials.sh [id ...]
#
# Point TRIALS_DIR under $TMPDIR: a workspace inside this repository or the
# home directory has AGENTS.md files above it, and evals.json and fixtures/
# within reach.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." > /dev/null && pwd)"

exec bash "$REPO_ROOT/evals/lib/run-mcp-trials.sh" "$SCRIPT_DIR" "$@"
