#!/usr/bin/env bash
# Build a design doc with three authors in its history. Only `git log` or
# `git blame` reveals which passages belong to whom: the file itself carries
# no bylines, exactly like a real collaborative document.
set -euo pipefail

commit_as() {
  local name="$1" email="$2" message="$3"
  git add -A
  GIT_AUTHOR_NAME="$name" GIT_AUTHOR_EMAIL="$email" \
  GIT_COMMITTER_NAME="$name" GIT_COMMITTER_EMAIL="$email" \
    git commit --quiet -m "$message"
}

# Priya opens the document. Formal, hedged, heavy on process language.
cat > docs/on-call-redesign.md <<'DOC'
# On-call redesign

## Background

Following the incident review, it was agreed that the current on-call
rotation should be revisited. This document has been prepared in order to
facilitate a discussion regarding possible alternatives, and it would be
beneficial if all stakeholders could review it prior to the planning session
so that we are able to align on a preferred direction.
DOC
commit_as "Priya Raman" "priya.raman@example.com" "Start on-call redesign doc"

# The user adds the problem statement. Blunt, concrete, numbers first.
cat >> docs/on-call-redesign.md <<'DOC'

## What is actually wrong

Three people cover 80% of the weekends. That is the whole problem. Everything
else in this document is a consequence of it.

The rotation is weekly, so a bad week is seven days long and there is no way
to hand it off halfway. Two of those three people have asked to come off the
rotation this quarter. If both leave, one person covers every weekend, and
that is not a rotation, it is a pager with someone's name taped to it.
DOC
commit_as "Alex Reyes" "eval-user@example.com" "Add problem statement"

# Jordan adds constraints. Different again: list-heavy, cautious.
cat >> docs/on-call-redesign.md <<'DOC'

## Constraints to keep in mind

- We cannot page anyone outside their own timezone without an opt-in.
- The billing service has only two people who can debug it at 3am.
- Any change needs a month of notice, per the team agreement.
- We should probably not change the rotation during the migration.
DOC
commit_as "Jordan Blake" "jordan.blake@example.com" "Add constraints"

# The user again, with the proposal. Same voice as the problem statement.
cat >> docs/on-call-redesign.md <<'DOC'

## What I want to do about it

Split the rotation into six, with a primary and a secondary. The secondary
exists so the primary can sleep, not so the primary can escalate.

This does not fix the billing service problem. Nothing fixes that except
teaching two more people, which takes a quarter and should start now rather
than after the rotation changes.
DOC
commit_as "Alex Reyes" "eval-user@example.com" "Add proposal"
