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

for run_dir in "$@"; do
  ws="$run_dir/workspace"
  [[ -d "$ws/.git" ]] || continue
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
