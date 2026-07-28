#!/usr/bin/env bash
# A pre-commit hook rejects commits that introduce trailing whitespace. The
# diff incidentally introduces a trailing-whitespace line, so the first
# commit attempt should fail and the skill is expected to fix the issue and
# retry (per SKILL.md step 7), not give up.
set -euo pipefail
cd "$1"

git checkout -b PROJ-403-fix-formatter-output --quiet

mkdir -p .git/hooks
cat > .git/hooks/pre-commit <<'HOOK'
#!/usr/bin/env bash
if git diff --cached --check | grep -q .; then
  echo "Trailing whitespace detected in staged changes. Commit rejected." >&2
  exit 1
fi
exit 0
HOOK
chmod +x .git/hooks/pre-commit

printf 'export function formatCurrency(amount: number): string {\n  if (amount < 0) {   \n    return `-$${Math.abs(amount).toFixed(2)}`;\n  }\n  return `$${amount.toFixed(2)}`;\n}\n' > src/formatter.ts
