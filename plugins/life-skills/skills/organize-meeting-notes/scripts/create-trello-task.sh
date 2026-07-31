#!/bin/bash

# Create a single Trello card for a meeting-notes action item.
# Usage: create-trello-task.sh "<action item text>" [--desc "<description>"]
# Run with -h or --help for full usage information
#
# On success, prints exactly one line to stdout: the created card's URL.
# On failure, prints an error to stderr and exits non-zero.
#
# Real mode requires TRELLO_API_KEY, TRELLO_TOKEN, and TRELLO_LIST_ID
# (the target list to add the card to) in the environment.
#
# Eval-only fixture mode: if TRELLO_FIXTURE_FILE is set, no real Trello API
# call is made. The fixture file is a JSON object with a "create_card" key,
# whose value is either a single response object (reused for every call) or
# a list of response objects consumed one per invocation. Each response
# object is {"url": "<card url>"} for success, or {"exit_code": N, "error":
# "<message>"} for a simulated failure. Call counts persist across
# invocations (each call is a fresh process) via a counts file at
# "$TRELLO_FIXTURE_COUNTS_DIR/$(basename "$TRELLO_FIXTURE_FILE").counts.json"
# if TRELLO_FIXTURE_COUNTS_DIR is set, else next to the fixture file itself --
# mirrors the SONAR_FIXTURE_FILE/SONAR_FIXTURE_COUNTS_DIR convention in
# resolve-sonarqube-issues/scripts/list-sonar-issues.py. If set,
# TRELLO_FIXTURE_LOG has one JSON line appended per call ({"text", "desc",
# "url"} on success) for graders, mirroring GH_STUB_LOG.

set -euo pipefail

DESC=""
TEXT=""

show_help() {
  echo "Usage: $0 \"<action item text>\" [--desc \"<description>\"]"
  echo ""
  echo "Description:"
  echo "  Creates a single Trello card for a meeting-notes action item and"
  echo "  prints the created card's URL on success."
  echo ""
  echo "Options:"
  echo "  --desc TEXT      Card description (source context: meeting title,"
  echo "                   date/time, and optionally topic/reason)."
  echo "  -h, --help       Show this help message"
  echo ""
  echo "Environment (real mode):"
  echo "  TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_LIST_ID"
  echo ""
  echo "Environment (eval fixture mode, see script header for full format):"
  echo "  TRELLO_FIXTURE_FILE, TRELLO_FIXTURE_COUNTS_DIR, TRELLO_FIXTURE_LOG"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --desc)
      if [[ $# -lt 2 ]]; then
        echo "Error: --desc requires a value." >&2
        exit 1
      fi
      DESC="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      if [[ -n "$TEXT" ]]; then
        echo "Error: unexpected extra argument: $1" >&2
        exit 1
      fi
      TEXT="$1"
      shift
      ;;
  esac
done

if [[ -z "$TEXT" ]]; then
  echo "Error: action item text is required. Use -h or --help for usage." >&2
  exit 1
fi

if [[ -n "${TRELLO_FIXTURE_FILE:-}" ]]; then
  RESULT=$(python3 - "$TRELLO_FIXTURE_FILE" "${TRELLO_FIXTURE_COUNTS_DIR:-}" <<'PYEOF'
import json
import os
import sys

fixture_file, counts_dir = sys.argv[1], sys.argv[2]

fixtures = json.loads(open(fixture_file).read())
if "create_card" not in fixtures:
    print(f"Error: TRELLO_FIXTURE_FILE {fixture_file} has no 'create_card' entry. "
          "Add one to the fixture's top-level object.", file=sys.stderr)
    sys.exit(1)

entry = fixtures["create_card"]
if not isinstance(entry, list):
    response = entry
else:
    if counts_dir:
        counts_path = os.path.join(counts_dir, os.path.basename(fixture_file) + ".counts.json")
    else:
        counts_path = fixture_file + ".counts.json"
    counts = {}
    if os.path.exists(counts_path):
        try:
            counts = json.loads(open(counts_path).read())
        except (json.JSONDecodeError, OSError):
            counts = {}
    idx = counts.get("create_card", 0)
    counts["create_card"] = idx + 1
    with open(counts_path, "w") as f:
        json.dump(counts, f)
    response = entry[min(idx, len(entry) - 1)]

if "url" in response:
    print("OK")
    print(response["url"])
else:
    print("FAIL")
    print(response.get("error", "fixture-simulated failure"))
    print(response.get("exit_code", 1))
PYEOF
)
  STATUS=$(echo "$RESULT" | sed -n '1p')
  if [[ "$STATUS" = "OK" ]]; then
    URL=$(echo "$RESULT" | sed -n '2p')
    if [[ -n "${TRELLO_FIXTURE_LOG:-}" ]]; then
      python3 - "$TRELLO_FIXTURE_LOG" "$TEXT" "$DESC" "$URL" <<'PYEOF'
import json
import sys

log_file, text, desc, url = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(log_file, "a") as f:
    f.write(json.dumps({"text": text, "desc": desc, "url": url}) + "\n")
PYEOF
    fi
    echo "$URL"
    exit 0
  else
    ERROR_MSG=$(echo "$RESULT" | sed -n '2p')
    EXIT_CODE=$(echo "$RESULT" | sed -n '3p')
    if [[ -n "${TRELLO_FIXTURE_LOG:-}" ]]; then
      python3 - "$TRELLO_FIXTURE_LOG" "$TEXT" "$DESC" "$ERROR_MSG" <<'PYEOF'
import json
import sys

log_file, text, desc, error = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(log_file, "a") as f:
    f.write(json.dumps({"text": text, "desc": desc, "error": error}) + "\n")
PYEOF
    fi
    echo "Error: $ERROR_MSG" >&2
    exit "$EXIT_CODE"
  fi
fi

# Real mode
if [[ -z "${TRELLO_API_KEY:-}" ]] || [[ -z "${TRELLO_TOKEN:-}" ]] || [[ -z "${TRELLO_LIST_ID:-}" ]]; then
  echo "Error: TRELLO_API_KEY, TRELLO_TOKEN, and TRELLO_LIST_ID must all be set." >&2
  exit 1
fi

RESPONSE=$(curl -sS -w "\n%{http_code}" -X POST "https://api.trello.com/1/cards" \
  --data-urlencode "key=${TRELLO_API_KEY}" \
  --data-urlencode "token=${TRELLO_TOKEN}" \
  --data-urlencode "idList=${TRELLO_LIST_ID}" \
  --data-urlencode "name=${TEXT}" \
  --data-urlencode "desc=${DESC}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -lt 200 ]] || [[ "$HTTP_CODE" -ge 300 ]]; then
  echo "Error: Trello API request failed (HTTP $HTTP_CODE): $BODY" >&2
  exit 1
fi

URL=$(echo "$BODY" | python3 -c "import json,sys; print(json.load(sys.stdin)['shortUrl'])")
echo "$URL"
