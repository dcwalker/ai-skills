#!/usr/bin/env bash
# Otherwise-clean diff that leaves a block of commented-out old code behind.
set -euo pipefail
cd "$1"

git checkout -b PROJ-406-simplify-parser --quiet

cat > src/parser.ts <<'EOF'
export function parseCsvLine(line: string): string[] {
  // function parseCsvLineOld(line) {
  //   var parts = line.split(",");
  //   var out = [];
  //   for (var i = 0; i < parts.length; i++) {
  //     out.push(parts[i].trim());
  //   }
  //   return out;
  // }
  return line.split(",").map((cell) => cell.trim().replace(/^"|"$/g, ""));
}
EOF
