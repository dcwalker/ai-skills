#!/usr/bin/env bash
# Leave an UNCOMMITTED modification to the skill's SKILL.md, so the local
# working-tree diff touches a skill file and Step 4b (Skill Quality Review)
# should fire for plan-weekly-review.
set -euo pipefail
WORKSPACE_DIR="${1:-$(pwd)}"
cd "$WORKSPACE_DIR"

cat >> plugins/life-skills/skills/plan-weekly-review/SKILL.md <<'EOF'

## Step 5: Schedule the first actions

Offer to place each priority's first action onto the user's calendar as a
concrete block. If the user declines, note the action in the plan's parking
list instead so it is not lost.
EOF
