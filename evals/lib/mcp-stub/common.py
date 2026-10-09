"""Shared helpers for eval-only MCP stub servers.

An MCP stub server is a real, protocol-compliant stdio MCP server (built on
the official `mcp` SDK) that a trial's scratch `.mcp.json` points Claude Code
at instead of the real third-party server, the same way `evals/lib/gh-stub/gh`
stands in for the real `gh` binary on PATH. Unlike `gh-stub` (a fresh process
per call, so `times` caps and call counts have to be persisted to a file via
GH_STUB_COUNTS_DIR), an MCP stub is one long-lived process for each
`claude` turn -- Claude Code launches it once and keeps the connection
open -- so it can just hold its fake backing state in memory for that
turn's duration. A
trial with follow-up turns starts a new process per turn; run-mcp-trials.sh
points each resumed turn's MCP_STUB_STATE_FILE at the previous turn's
MCP_STUB_STATE_OUT, so state carries across turns.

State model: a stub's backing "database" is a plain JSON object (shape is
stub-specific, e.g. trello_stub.py's is {"boards", "lists", "cards",
"labels"}). It's seeded at startup from MCP_STUB_STATE_FILE and mutated
in place as tools are called. State is flushed to MCP_STUB_STATE_OUT after
every tool call (not only on clean shutdown), so a grader can diff final
state against an expected snapshot even if the trial's `claude` subprocess
is killed on timeout rather than exiting cleanly.

Call logging: if MCP_STUB_LOG is set, every tool call is appended as one JSON
line ({"tool": name, "args": {...}, "result": ...}) -- mirrors GH_STUB_LOG's
role of letting a grader assert on call sequence/arguments in addition to
final state, without constraining the exact path taken to get there.

Scheduled changes (opt-in, every stub): a state file may carry a top-level
"scheduled_changes" list, which changes the state partway through a trial,
standing in for another person or an automation editing the service while
the skill works. Each entry is

  {"id": "card-2-done-elsewhere",
   "after_call": {"tool": "view_list", "count": 1,
                  "args": {"list_id": "list-1"}},
   "changes": [{"op": "set", "path": ["cards", "card-2", "list_id"],
                "value": "list-3"}]}

- "after_call" is the trigger: the entry fires right after the count-th call
  to the named tool (count defaults to 1). The optional "args" counts only
  calls whose logged arguments include each of those keys with exactly that
  value. A call counts once the stub has logged it, so calls a stub logs and
  then refuses count too. The triggering call's own response is unchanged:
  it was built before the entry fired, so the change shows from the next
  call on.
- "changes" are applied in order. Each "path" is a list of keys (strings for
  objects, integers for lists) from the state's root. "set" puts "value" at
  the path, creating the last key if needed; "merge" shallow-updates the
  object at the path with "value"'s keys; "append" adds "value" to the list
  at the path; "delete" removes the path.
- Each entry fires at most once. The stub records its progress in the entry
  itself, as "calls_seen" and "fired", and flushes the state, so a resumed
  turn, seeded from MCP_STUB_STATE_OUT, carries on counting rather than
  starting over or firing a second time. Those two keys and the
  "scheduled_changes" list itself are harness bookkeeping, not service data:
  leave them out of a state diff. The changes themselves are not the
  skill's writes either, so a grader diffing final state against the seed
  should first apply the fired entries' changes to the seed.
- Firing is logged in MCP_STUB_LOG as its own line, in the same shape as a
  call: {"tool": "_scheduled_change", "args": {"id": ..., "after_call":
  {...}}, "result": {"changes": [...]}} right after the triggering call's
  line, so a grader can see exactly when the state moved. No real tool
  starts with an underscore, so the line cannot be mistaken for a call.
- Validation is up front: at startup the stub applies every unfired entry,
  in order, to a throwaway copy of the state, and refuses to start if one
  names an unknown op or a path that does not exist, so a mistyped fixture
  fails loudly instead of never firing. A resumed turn, whose state file is
  the previous turn's state-out, checks only each entry's shape. A change
  that no longer applies when it fires (the skill deleted its target first)
  is logged with an "error" in place of "changes" and skipped.
- fixture-dates.py moves dates inside "changes" like any other part of the
  state: ISO values shift and {{date:...}} tokens resolve. A Slack "ts" or
  "thread_ts" value shifts only under a key of that name, so set the message
  object that holds it ("set" on the message, or "merge" with a dict naming
  "ts") rather than "set" with the bare timestamp as "value".
"""

import copy
import json
import os
import threading

SCHEDULED_CHANGE_TOOL = "_scheduled_change"
_CHANGE_OPS = {"set", "merge", "append", "delete"}


def _walk(data, path: list):
    """The container holding the path's last key, and that key."""
    node = data
    for key in path[:-1]:
        node = node[key]
    return node, path[-1]


def _apply_change(data, change: dict) -> None:
    op, path = change.get("op"), change.get("path")
    if op not in _CHANGE_OPS:
        raise ValueError(f"unknown op {op!r}; use one of {sorted(_CHANGE_OPS)}")
    if not isinstance(path, list) or not path:
        raise ValueError(f"path must be a non-empty list of keys, not {path!r}")
    if op != "delete" and "value" not in change:
        raise ValueError(f"op {op!r} needs a value")
    parent, key = _walk(data, path)
    if op == "set":
        parent[key] = copy.deepcopy(change["value"])
    elif op == "delete":
        del parent[key]
    elif op == "merge":
        target = parent[key]
        if not isinstance(target, dict) or not isinstance(change["value"], dict):
            raise ValueError(f"merge needs an object at {path!r} and an object value")
        target.update(copy.deepcopy(change["value"]))
    else:
        target = parent[key]
        if not isinstance(target, list):
            raise ValueError(f"append needs a list at {path!r}")
        target.append(copy.deepcopy(change["value"]))


def _call_matches(trigger: dict, tool: str, args: dict) -> bool:
    if trigger.get("tool") != tool:
        return False
    wanted = trigger.get("args") or {}
    return all(isinstance(args, dict) and args.get(k) == v for k, v in wanted.items())


def _check_entry_shape(entry: dict, ids: set) -> str:
    """Raise unless a scheduled-change entry is well formed; record its id in
    `ids` and return it."""
    if not isinstance(entry, dict):
        raise ValueError(f"scheduled change must be an object, got {entry!r}")
    name = entry.get("id")
    if not name or name in ids:
        raise ValueError(f"scheduled change needs a unique id, got {name!r}")
    ids.add(name)
    trigger = entry.get("after_call")
    if not isinstance(trigger, dict) or not trigger.get("tool"):
        raise ValueError(f"scheduled change {name!r} needs after_call.tool")
    count = trigger.get("count", 1)
    if not isinstance(count, int) or count < 1:
        raise ValueError(f"scheduled change {name!r}: after_call.count must be a positive integer")
    if not isinstance(entry.get("changes"), list) or not entry["changes"]:
        raise ValueError(f"scheduled change {name!r} needs a non-empty changes list")
    return name


class StubState:
    """In-memory state for one MCP stub server process, with load/flush/log."""

    def __init__(self, default: dict):
        # Reentrant: log_call flushes while holding it.
        self._lock = threading.RLock()
        state_file = os.environ.get("MCP_STUB_STATE_FILE")
        if state_file and os.path.exists(state_file):
            with open(state_file) as f:
                self.data = json.load(f)
        else:
            self.data = default
        self._state_out = os.environ.get("MCP_STUB_STATE_OUT")
        self._log_file = os.environ.get("MCP_STUB_LOG")
        self._check_schedule()
        self.flush()

    def _schedule(self) -> list:
        schedule = self.data.get("scheduled_changes") or []
        if not isinstance(schedule, list):
            raise ValueError("scheduled_changes must be a list")
        return schedule

    def _check_schedule(self) -> None:
        """Refuse to start on a schedule that could never apply as written.
        A resumed turn (the driver seeds it from MCP_STUB_STATE_OUT) checks
        only the entries' shape: the skill may already have removed a
        pending change's target, which is logged and skipped when it fires,
        not a reason to start without the server."""
        state_file = os.environ.get("MCP_STUB_STATE_FILE")
        resumed = bool(state_file) and state_file == os.environ.get("MCP_STUB_STATE_OUT")
        trial = copy.deepcopy(self.data)
        ids = set()
        for entry in self._schedule():
            name = _check_entry_shape(entry, ids)
            if entry.get("fired") or resumed:
                continue
            for change in entry["changes"]:
                try:
                    _apply_change(trial, change)
                except (KeyError, IndexError, TypeError, ValueError) as e:
                    raise ValueError(f"scheduled change {name!r} cannot apply {change!r}: {e}") from e

    def _write_log(self, line: dict) -> None:
        if self._log_file:
            with open(self._log_file, "a") as f:
                f.write(json.dumps(line) + "\n")

    def _advance_schedule(self, tool: str, args: dict) -> bool:
        """Count this call against each pending entry; fire those it completes.
        True when any entry's bookkeeping moved, so the state needs a flush."""
        moved = False
        for entry in self._schedule():
            if entry.get("fired") or not _call_matches(entry["after_call"], tool, args):
                continue
            entry["calls_seen"] = entry.get("calls_seen", 0) + 1
            moved = True
            if entry["calls_seen"] < entry["after_call"].get("count", 1):
                continue
            entry["fired"] = True
            staged = copy.deepcopy({k: v for k, v in self.data.items() if k != "scheduled_changes"})
            try:
                for change in entry["changes"]:
                    _apply_change(staged, change)
            except (KeyError, IndexError, TypeError, ValueError) as e:
                outcome = {"error": f"{type(e).__name__}: {e}"}
            else:
                staged["scheduled_changes"] = self.data.get("scheduled_changes")
                self.data.clear()
                self.data.update(staged)
                outcome = {"changes": entry["changes"]}
            self._write_log({"tool": SCHEDULED_CHANGE_TOOL,
                             "args": {"id": entry["id"], "after_call": entry["after_call"]},
                             "result": outcome})
        return moved

    def flush(self) -> None:
        """Write current state to MCP_STUB_STATE_OUT, if set."""
        if not self._state_out:
            return
        with self._lock:
            with open(self._state_out, "w") as f:
                json.dump(self.data, f, indent=2)

    def log_call(self, tool: str, args: dict, result) -> None:
        """Append one call to MCP_STUB_LOG, if set, then apply any scheduled
        change this call triggers (see the module docstring). Call after
        mutating state and before returning, so the log and
        MCP_STUB_STATE_OUT snapshot at any point in the log are consistent
        with each other."""
        with self._lock:
            self._write_log({"tool": tool, "args": args, "result": result})
            if self._advance_schedule(tool, args):
                self.flush()
