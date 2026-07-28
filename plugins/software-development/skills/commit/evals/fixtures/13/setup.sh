#!/usr/bin/env bash
# Single-concern refactor (rename a field) applied consistently across three
# files. Multiple files touched, but one coherent concern -- should be one
# commit, not a request to split.
set -euo pipefail
cd "$1"

git checkout -b PROJ-407-rename-user-model --quiet

cat > src/models/user.ts <<'EOF'
export interface User {
  id: string;
  displayName: string;
}
EOF

cat > src/services/userService.ts <<'EOF'
import type { User } from "../models/user";

export function formatUserLabel(user: User): string {
  return user.displayName;
}
EOF

cat > src/controllers/userController.ts <<'EOF'
import { formatUserLabel } from "../services/userService";
import type { User } from "../models/user";

export function renderUser(user: User): string {
  return `<span>${formatUserLabel(user)}</span>`;
}
EOF
