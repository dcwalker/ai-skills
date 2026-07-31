"""Shared helpers for eval-only MCP stub servers.

An MCP stub server is a real, protocol-compliant stdio MCP server (built on
the official `mcp` SDK) that a trial's scratch `.mcp.json` points Claude Code
at instead of the real third-party server, the same way `evals/lib/gh-stub/gh`
stands in for the real `gh` binary on PATH. Unlike `gh-stub` (a fresh process
per call, so `times` caps and call counts have to be persisted to a file via
GH_STUB_COUNTS_DIR), an MCP stub is one long-lived process for the whole
trial -- Claude Code launches it once and keeps the connection open -- so it
can just hold its fake backing state in memory for the trial's duration.

State model: a stub's backing "database" is a plain JSON object (shape is
stub-specific, e.g. trello_stub.py's is {"boards", "lists", "cards",
"labels"}). It's seeded once at startup from MCP_STUB_STATE_FILE and mutated
in place as tools are called. State is flushed to MCP_STUB_STATE_OUT after
every tool call (not only on clean shutdown), so a grader can diff final
state against an expected snapshot even if the trial's `claude` subprocess
is killed on timeout rather than exiting cleanly.

Call logging: if MCP_STUB_LOG is set, every tool call is appended as one JSON
line ({"tool": name, "args": {...}, "result": ...}) -- mirrors GH_STUB_LOG's
role of letting a grader assert on call sequence/arguments in addition to
final state, without constraining the exact path taken to get there.
"""

import json
import os
import threading


class StubState:
    """In-memory state for one MCP stub server process, with load/flush/log."""

    def __init__(self, default: dict):
        self._lock = threading.Lock()
        state_file = os.environ.get("MCP_STUB_STATE_FILE")
        if state_file and os.path.exists(state_file):
            with open(state_file) as f:
                self.data = json.load(f)
        else:
            self.data = default
        self._state_out = os.environ.get("MCP_STUB_STATE_OUT")
        self._log_file = os.environ.get("MCP_STUB_LOG")
        self.flush()

    def flush(self) -> None:
        """Write current state to MCP_STUB_STATE_OUT, if set."""
        if not self._state_out:
            return
        with self._lock:
            with open(self._state_out, "w") as f:
                json.dump(self.data, f, indent=2)

    def log_call(self, tool: str, args: dict, result) -> None:
        """Append one call to MCP_STUB_LOG, if set. Call after mutating state
        and before returning, so the log and MCP_STUB_STATE_OUT snapshot at
        any point in the log are consistent with each other."""
        if not self._log_file:
            return
        with self._lock:
            with open(self._log_file, "a") as f:
                f.write(json.dumps({"tool": tool, "args": args, "result": result}) + "\n")
