#!/usr/bin/env bash
# Report contamination of a finished trial by the ORCHESTRATING session.
#
# Usage: check-trial-hygiene.sh <run-dir> [<run-dir> ...]
#
# A trial's output should be a product of the skill under test and the
# fixture -- nothing else. But an executor is usually an agent running under
# its own system prompt, and that prompt can carry conventions of its own. The
# observed case: a session whose instructions say to end every commit message
# with `Co-Authored-By: Claude ...` / `Claude-Session: ...` produced fixture
# commits carrying those trailers, in a `commit` benchmark, where the commit
# message IS the artifact being graded.
#
# It fired in 2 of 13 trials rather than all 13, which is the worse failure:
# a constant offset is at least visible in every row, while an intermittent
# one just looks like variance in the skill.
#
# Prevention is the executor prompt (see evals/README.md). This is the backstop
# that makes a prevention failure visible instead of silent, so run it over the
# run dirs before writing a baseline.
#
# Exit 0 = clean, 1 = contamination found, 2 = bad usage.
set -uo pipefail

if [[ $# -eq 0 ]]; then
  echo "usage: check-trial-hygiene.sh <run-dir> [<run-dir> ...]" >&2
  exit 2
fi

# Trailers that belong to a Claude Code session rather than to any skill.
SESSION_TRAILERS='Claude-Session:|Co-Authored-By: Claude|Generated with \[Claude Code\]'

found=0
checked=0

skipped=()

for run_dir in "$@"; do
  ws="$run_dir/workspace"
  if [[ ! -d "$ws/.git" ]]; then
    skipped+=("$run_dir")
    continue
  fi
  checked=$((checked + 1))

  # Only commits the trial added; the fixture's own base commit is not its doing.
  base="$(git -C "$ws" rev-list --max-parents=0 HEAD 2>/dev/null | head -1)"
  [[ -n "$base" ]] || continue
  range="$base..HEAD"

  while read -r sha; do
    [[ -n "$sha" ]] || continue
    if git -C "$ws" log -1 --format=%B "$sha" | grep -qE "$SESSION_TRAILERS"; then
      hit="$(git -C "$ws" log -1 --format=%B "$sha" | grep -oE "$SESSION_TRAILERS" | sort -u | tr '\n' ' ')"
      echo "$(basename "$run_dir"): commit ${sha:0:7} carries session trailer(s): $hit"
      found=$((found + 1))
    fi
  done < <(git -C "$ws" rev-list "$range" 2>/dev/null)
done

# Checking nothing is not the same as finding nothing, and this script exists
# precisely to stop a silent pass. `check-trial-hygiene.sh .../eval-*` is the
# documented invocation, and bash leaves a non-matching glob as a literal, so a
# typo or a run that never created its workspaces would otherwise print "clean:
# ... in 0 trial(s)" and exit 0 -- the same answer as a real all-clear.
if [[ $checked -eq 0 ]]; then
  echo "check-trial-hygiene: no run dir with a workspace/.git among: $*" >&2
  echo "check-trial-hygiene: checked nothing, so this is not a pass." >&2
  exit 2
fi

# A partial run is a weaker version of the same trap: 3 of 13 checked still
# reports "clean". Name what was skipped so the count cannot be read as total.
if [[ ${#skipped[@]} -gt 0 ]]; then
  echo "warning: ${#skipped[@]} argument(s) had no workspace/.git and were not checked:" >&2
  for s in "${skipped[@]}"; do echo "  $s" >&2; done
fi

if [[ $found -gt 0 ]]; then
  echo
  echo "$found contaminated commit(s) across $checked trial(s)."
  echo "These trailers came from the executor's own session, not the skill under"
  echo "test. Re-run the affected trials with the executor prompt clause in"
  echo "evals/README.md ('What an executor must be told'), and do not publish a"
  echo "baseline whose commit messages are partly the harness's doing."
  exit 1
fi

echo "clean: no session trailers in $checked trial(s)"
