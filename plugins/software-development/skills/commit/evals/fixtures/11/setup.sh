#!/usr/bin/env bash
# Adds a new API endpoint but leaves openapi.yaml unchanged. The skill
# should notice the API spec is now out of date.
set -euo pipefail
cd "$1"

git checkout -b PROJ-405-add-export-endpoint --quiet

cat > src/routes.ts <<'EOF'
export const ROUTES = {
  "GET /users": "listUsers",
  "GET /users/:id": "getUser",
  "POST /users/:id/export": "exportUser",
};
EOF
