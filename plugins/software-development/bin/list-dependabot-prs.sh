#!/bin/bash

# Shim: forwards to the real script bundled with the update-dependabot-bulk skill.
#
# Claude Code appends <plugin-root>/bin to PATH for every installed plugin, so
# this shim is what makes the plain 'list-dependabot-prs.sh' invocation work.
# The real script stays under skills/ so each skill's bundled resources remain
# together.
#
# The plugin root is resolved relative to this file rather than hard-coded: the
# install path contains a commit hash that changes on every plugin update.

BIN_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
PLUGIN_ROOT=$(cd -- "$BIN_DIR/.." && pwd)
TARGET="$PLUGIN_ROOT/skills/update-dependabot-bulk/scripts/list-dependabot-prs.sh"

if [ ! -f "$TARGET" ]; then
  echo "Error: could not find $TARGET" >&2
  exit 1
fi

exec "$TARGET" "$@"
