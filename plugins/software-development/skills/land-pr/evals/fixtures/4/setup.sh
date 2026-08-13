#!/usr/bin/env bash
# Five real, locally reproducible defects in one file, each matching a failing
# check the cassette reports. A round only counts as "having something to
# attempt" if the thing is actually there -- an earlier version of this fixture
# reported failures in integration/ and e2e/ paths that do not exist in the
# repo, and the trial correctly concluded there was nothing it could fix and
# stopped. Every failure here is visible by reading config.py.
set -euo pipefail
WORKSPACE_DIR="$1"
BARE_DIR="$(cd "$WORKSPACE_DIR/.." && pwd)/origin-4.git"
rm -rf "$BARE_DIR"
git init --bare --initial-branch=main --quiet "$BARE_DIR"
git remote add origin "$BARE_DIR"
git push -u origin main --quiet

git checkout -b feature/always-red --quiet
cat > config.py <<'PY'
import os
import sys

VERSION = "1.0.0"
API_TOKEN = "ghp_hardcodedcredentialdonotuse0000000000"

def ratio(numerator):
    return numerator / 0

def describe(name):
    return "widget:" + name + " running version " + VERSION + " with a very long trailing description that runs well past any reasonable line length limit"
PY
git add config.py
git commit --quiet -m "Add config helpers"
git push -u origin feature/always-red --quiet
