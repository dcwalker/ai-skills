#!/usr/bin/env python3
"""Move a stub fixture's dates to the run date, so an eval does not age.

A fixture written on 31 July around "the fair on 19 September" reads very
differently when the suite runs in October: the fair has passed, and a trial
reasonably stops to ask whether the item still stands. The suite then
measures the calendar instead of the skill. This script keeps every date in
a fixture where its author put it relative to the day it was written.

A fixture opts in by giving each of its *-mcp-state.json files a top-level
"anchor_date": the date the scenario was written for (YYYY-MM-DD). Every
state file in one fixture directory must name the same anchor. The shift is
the gap from the anchor to the run date, rounded down to whole weeks so a
weekday stays right: "Thursday, Oct 8" is still a Thursday after the move.

What moves:

- Structured values, wherever they sit in the state: an ISO date
  (2026-09-19), an ISO datetime (2026-09-19T09:00:00Z, with or without
  seconds, fraction, or offset), a display datetime (2026-09-27 09:14:00 PDT,
  the Slack stub's rendering), and a Slack timestamp (1790525640.000100)
  under a "ts" or "thread_ts" key. A display datetime keeps its time and zone
  label as written, so one that crosses a daylight-saving change is an hour
  off its timestamp; nothing the evals grade depends on that hour.
- Dates in prose, written as tokens and replaced with the moved date:
    {{date:2026-09-19|%B %-d}}     ->  November 21
    {{date:2026-09-01|%B}}         ->  November
    {{date:2026-09-19}}            ->  2026-11-21 (ISO when no format)
    {{slackts:1790525640.000100}}  ->  the moved Slack timestamp
    {{slackp:1790525640.000100}}   ->  the moved timestamp as a permalink's
                                       p-segment: "p", then its digits
  Formats are Python strftime, plus %Q for the northern-hemisphere season
  ("autumn") and %q for the same with "fall" for autumn. A format starting
  with "^" capitalizes the result's first letter: {{date:2026-10-01|^%q}}
  gives "Fall". A weekday name written as plain text needs no token, since
  the whole-week shift keeps it true.

A fixture with no anchor loads unchanged, and a token in a fixture with no
anchor is an error rather than a silent no-op. The run date is today, or
EVAL_RUN_DATE (YYYY-MM-DD) when set, so a run can be reproduced exactly.

Usage:
  fixture-dates.py state <fixture-dir> <state.json> <out.json>
      Write the resolved state, with "anchor_date" removed.
  fixture-dates.py eval <evals.json> <eval-id> <fixture-dir> <out.json>
      Write that eval's entry with tokens in expected_output and
      expectations resolved, for graders. Tokens are not allowed in the
      prompt, which the drivers read before this script runs.
"""

from __future__ import annotations

import datetime
import glob
import json
import os
import re
import sys
import tempfile

# A dated value is a YYYY-MM-DD prefix and an optional time part. The time
# part is checked separately, which keeps each pattern simple.
DATED = re.compile(r"^(\d{4}-\d{2}-\d{2})(.*)$")
TIME_PARTS = (
    re.compile(r"^$"),                                       # 2026-09-19
    re.compile(r"^T\d{2}:\d{2}(:\d{2})?(\.\d+)?$"),           # ...T09:00:00
    re.compile(r"^T\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})$"),  # with a zone
    re.compile(r"^ \d{2}:\d{2}:\d{2}( [A-Z]{2,5})?$"),         # 2026-09-27 09:14:00 PDT
)
SLACK_TS = re.compile(r"^(\d{9,10})\.(\d{6})$")
SLACK_TS_KEYS = {"ts", "thread_ts"}
TOKEN = re.compile(r"\{\{(date|slackts|slackp):([^}|]+)(?:\|([^}]*))?\}\}")


def fail(message: str) -> None:
    print(f"fixture-dates: {message}", file=sys.stderr)
    sys.exit(1)


def run_date() -> datetime.date:
    override = os.environ.get("EVAL_RUN_DATE")
    if not override:
        return datetime.date.today()
    try:
        return datetime.date.fromisoformat(override)
    except ValueError:
        fail(f"EVAL_RUN_DATE must be YYYY-MM-DD, not {override!r}")


def fixture_anchor(fixture_dir: str) -> datetime.date | None:
    """The one anchor every state file in the fixture names, or None."""
    anchors = {}
    for path in sorted(glob.glob(os.path.join(fixture_dir, "*-mcp-state.json"))):
        with open(path) as fh:
            anchors[os.path.basename(path)] = json.load(fh).get("anchor_date")
    named = {a for a in anchors.values() if a is not None}
    if not named:
        return None
    if len(named) > 1 or None in anchors.values():
        fail(f"state files in {fixture_dir} must all name the same anchor_date: {anchors}")
    try:
        return datetime.date.fromisoformat(named.pop())
    except ValueError:
        fail(f"anchor_date in {fixture_dir} must be YYYY-MM-DD")


def shift_days(anchor: datetime.date | None) -> int:
    if anchor is None:
        return 0
    return (run_date() - anchor).days // 7 * 7


def moved(date_text: str, days: int) -> datetime.date:
    return datetime.date.fromisoformat(date_text) + datetime.timedelta(days=days)


SEASONS = {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
           6: "summer", 7: "summer", 8: "summer", 9: "autumn", 10: "autumn", 11: "autumn"}


def format_date(date: datetime.date, fmt: str) -> str:
    capitalize = fmt.startswith("^")
    fmt = fmt.lstrip("^")
    season = SEASONS[date.month]
    fmt = fmt.replace("%Q", season).replace("%q", "fall" if season == "autumn" else season)
    text = date.strftime(fmt)
    return text[:1].upper() + text[1:] if capitalize else text


def resolve_tokens(text: str, days: int, anchored: bool) -> str:
    def replace(match: re.Match) -> str:
        if not anchored:
            fail(f"token {match.group(0)!r} in a fixture with no anchor_date")
        kind, value, fmt = match.group(1), match.group(2).strip(), match.group(3)
        if kind == "date":
            date = moved(value, days)
            return format_date(date, fmt) if fmt else date.isoformat()
        ts = SLACK_TS.match(value)
        if not ts:
            fail(f"{match.group(0)!r} needs a Slack timestamp like 1790525640.000100")
        seconds = int(ts.group(1)) + days * 86400
        return f"{seconds}.{ts.group(2)}" if kind == "slackts" else f"p{seconds}{ts.group(2)}"
    return TOKEN.sub(replace, text)


def shift_structured(value: str, days: int, key: str | None) -> str | None:
    """The value moved, when the whole of it is a date, datetime, or Slack ts."""
    dated = DATED.match(value)
    if dated and any(part.match(dated.group(2)) for part in TIME_PARTS):
        return moved(dated.group(1), days).isoformat() + dated.group(2)
    ts = SLACK_TS.match(value)
    if ts and key in SLACK_TS_KEYS:
        return f"{int(ts.group(1)) + days * 86400}.{ts.group(2)}"
    return None


def resolve_value(value, days: int, anchored: bool, key: str | None = None):
    if isinstance(value, dict):
        return {k: resolve_value(v, days, anchored, k) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_value(v, days, anchored, key) for v in value]
    if not isinstance(value, str):
        return value
    shifted = shift_structured(value, days, key) if days else None
    return shifted if shifted is not None else resolve_tokens(value, days, anchored)


# The repository holding this script: evals/lib/fixture-dates.py, two levels up.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def allowed_roots() -> list[str]:
    """Where this script may read or write: the user's home, $TMPDIR, and this repo.

    The repo is listed because fixtures are read from it, and a checkout need
    not sit under the home directory: a cloud container clones to /home/user
    while HOME is /root.
    """
    roots = {os.path.expanduser("~"), tempfile.gettempdir(), REPO_ROOT}
    return sorted({os.path.realpath(root) for root in roots if os.path.isdir(root)})


def contained_path(path: str, what: str) -> str:
    """The resolved path, refused unless it lies under the home, temp, or repo directory.

    The harness passes these paths in, and a trial's own run directory can be
    anywhere TRIALS_DIR points, so a mistyped one must not read or overwrite
    files elsewhere.
    """
    resolved = os.path.realpath(os.path.expanduser(path))
    for root in allowed_roots():
        if resolved == root or resolved.startswith(root + os.sep):
            return resolved
    fail(f"{what} must be inside your home directory, {tempfile.gettempdir()}, or {REPO_ROOT}; got {path!r}")


def resolve_state(fixture_dir: str, state_path: str) -> dict:
    anchor = fixture_anchor(fixture_dir)
    with open(contained_path(state_path, "the state file")) as fh:
        state = json.load(fh)
    state.pop("anchor_date", None)
    return resolve_value(state, shift_days(anchor), anchor is not None)


def resolve_eval(evals_path: str, eval_id: str, fixture_dir: str) -> dict:
    with open(contained_path(evals_path, "evals.json")) as fh:
        entry = next((e for e in json.load(fh)["evals"] if str(e["id"]) == eval_id), None)
    if entry is None:
        fail(f"no eval {eval_id} in {evals_path}")
    if TOKEN.search(entry.get("prompt", "")):
        fail(f"eval {eval_id}'s prompt has a date token; tokens belong in fixtures and expectations")
    anchor = fixture_anchor(fixture_dir)
    resolved = resolve_value(entry, shift_days(anchor), anchor is not None)
    resolved["run_date"] = run_date().isoformat()
    resolved["shift_days"] = shift_days(anchor)
    return resolved


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 4 and args[0] == "state":
        resolved = resolve_state(contained_path(args[1], "the fixture directory"), args[2])
        out_path = args[3]
    elif len(args) == 5 and args[0] == "eval":
        resolved = resolve_eval(args[1], args[2], contained_path(args[3], "the fixture directory"))
        out_path = args[4]
    else:
        fail("usage: fixture-dates.py state <fixture-dir> <state.json> <out.json> | "
             "eval <evals.json> <eval-id> <fixture-dir> <out.json>")
    with open(contained_path(out_path, "the output file"), "w") as fh:
        json.dump(resolved, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
