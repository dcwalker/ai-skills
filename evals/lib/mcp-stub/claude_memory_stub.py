#!/usr/bin/env python3
"""Eval-only fake Claude app memory MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the six memory tools a Claude app chat has for the user's
memory: memory_list, memory_read, memory_write, memory_str_replace,
memory_append, and memory_delete. sync-memory's app-sync procedure
uses them to compare the shared memory tree with app memory and write
approved changes. See common.py's module docstring for the general
stub-server design.

Schema fidelity: tool names, parameter names, and behavior were taken from a
live Claude app chat on 2026-11-09, where Claude listed its memory tools and
their parameters, wrote a file with if_version "new", read it back
byte for byte, and deleted it with its version token:
  - memory_read(path): path is a string or a list of up to 20 paths; returns
    each file's content, last-updated time, and a 12-character version token.
  - memory_list(path_prefix?, cursor?, include_preview?): files sorted by
    path with size and last-updated time; include_preview adds a one-line
    preview from the description.
  - memory_write(path, content, if_version): creates or replaces a whole
    file; if_version is the token from the latest read or write, or "new"
    for a file that does not exist. A stale token is a conflict, not an
    overwrite.
  - memory_str_replace(path, old_str, new_str, if_version): old_str must
    occur exactly once; an empty new_str deletes it.
  - memory_append(path, content, if_version): adds content on a new line;
    if_version may be "new" to create the file.
  - memory_delete(path, if_version): removes a file; needs the token.
  - Locations are fixed: /profile.md, /preferences.md, /topics/<x>.md,
    /areas/<x>.md, /people/<x>.md. Files are capped at 49,152 bytes.
Not observable live, so flagged UNVERIFIED where built: the exact wording
of every response and error, the listing's layout, the cursor's page size,
and whether a write outside the fixed locations is refused (assumed yes).

State model (the fake memory store):
  {
    "files": {"/profile.md": {"content": "---\\nname: profile\\n...",
                              "version": "a1b2c3d4e5f6",
                              "updated": "2026-11-01T17:00:00Z"}}
  }

Every write gives the file a new version token derived from its path, its
content, and a per-store counter, so two writes of the same content still
change the token. A scheduled change (common.py) can rewrite a file between
the skill's read and its write; set its "version" too, so the skill's held
token goes stale exactly as it would when the app's background filing
edits a file.

Environment: MCP_STUB_STATE_FILE / MCP_STUB_STATE_OUT / MCP_STUB_LOG, same
contract as trello_stub.py.
"""

import datetime
import hashlib
import re

from common import StubState

state = StubState(default={"files": {}, "writes": 0})

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer("claude-memory-stub")

FILE_BYTE_CAP = 49152
LOCATION_RE = re.compile(r"^/(profile\.md|preferences\.md|(topics|areas|people)/[^/]+\.md)$")
PAGE_SIZE = 50  # UNVERIFIED


def _files() -> dict:
    return state.data["files"]


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_version(path: str, content: str) -> str:
    state.data["writes"] = state.data.get("writes", 0) + 1
    seed = f"{path}\0{content}\0{state.data['writes']}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def _check_location(path: str) -> None:
    if not LOCATION_RE.match(path):
        # UNVERIFIED: that the live store refuses other locations, and the wording.
        raise ValueError(f"claude-memory-stub: {path!r} is not a memory location (/profile.md, "
                         "/preferences.md, /topics/<name>.md, /areas/<name>.md, /people/<name>.md)")


def _check_version(path: str, if_version: str) -> None:
    existing = _files().get(path)
    if if_version == "new":
        if existing is not None:
            raise ValueError(f"claude-memory-stub: conflict: {path} already exists at version "
                             f"{existing['version']}; read it and pass that version")  # UNVERIFIED wording
        return
    if existing is None:
        raise ValueError(f"claude-memory-stub: {path} does not exist; pass if_version \"new\" to create it")
    if if_version != existing["version"]:
        raise ValueError(f"claude-memory-stub: conflict: {path} changed since version {if_version}; it is "
                         f"now at {existing['version']}. Read it again before writing.")  # UNVERIFIED wording


def _store(path: str, content: str) -> str:
    size = len(content.encode("utf-8"))
    if size > FILE_BYTE_CAP:
        raise ValueError(f"claude-memory-stub: {path} would be {size} bytes, over the {FILE_BYTE_CAP}-byte cap")
    version = _new_version(path, content)
    _files()[path] = {"content": content, "version": version, "updated": _now()}
    state.flush()
    # UNVERIFIED layout; the live write reported its version and "600 of 49,152 bytes".
    return f"Wrote {path} at version {version}, {size} of {FILE_BYTE_CAP:,} bytes."


def _description(content: str) -> str:
    for line in content.splitlines():
        if line.startswith("description:"):
            return line.removeprefix("description:").strip().strip("\"'")
    return ""


@server.tool()
def memory_list(path_prefix: str = "", cursor: str | None = None, include_preview: bool = False) -> str:
    """List memory files sorted by path, with size and last-updated time. path_prefix filters by
    directory, cursor pages through large stores, and include_preview adds a one-line preview taken
    from each file's description."""
    paths = sorted(p for p in _files() if p.startswith(path_prefix or ""))
    start = int(cursor) if cursor else 0
    page = paths[start:start + PAGE_SIZE]
    lines = []
    for path in page:
        entry = _files()[path]
        line = f"{path} ({len(entry['content'].encode('utf-8'))} bytes, updated {entry['updated']})"
        if include_preview:
            line += f" - {_description(entry['content'])}"
        lines.append(line)
    if start + PAGE_SIZE < len(paths):
        lines.append(f"[next cursor: {start + PAGE_SIZE}]")
    result = "\n".join(lines) if lines else "No memory files."  # UNVERIFIED wording
    state.log_call("memory_list", {"path_prefix": path_prefix, "cursor": cursor,
                                   "include_preview": include_preview}, result)
    return result


@server.tool()
def memory_read(path: str | list[str]) -> str:
    """Read one memory file, or a list of up to 20. Returns each file's content with its
    last-updated time, size, and version token; pass that token as if_version to change the
    file."""
    paths = [path] if isinstance(path, str) else list(path)
    if not 1 <= len(paths) <= 20:
        raise ValueError("claude-memory-stub: memory_read takes 1 to 20 paths")
    parts = []
    for one in paths:
        entry = _files().get(one)
        if entry is None:
            parts.append(f"{one}: not found")  # UNVERIFIED wording
            continue
        size = len(entry["content"].encode("utf-8"))
        parts.append(f"{one}\n[updated: {entry['updated']}] [size: {size}] [version: {entry['version']}]\n"
                     f"{entry['content']}")
    result = "\n\n".join(parts)
    state.log_call("memory_read", {"path": path}, result)
    return result


@server.tool()
def memory_write(path: str, content: str, if_version: str) -> str:
    """Create a memory file or replace it entirely. if_version is the 12-character version token
    from the latest read or write of this file, or "new" for a file that doesn't exist yet. A
    stale token is a conflict: nothing is written."""
    args = {"path": path, "content": content, "if_version": if_version}
    try:
        _check_location(path)
        _check_version(path, if_version)
        result = _store(path, content)
    except ValueError as error:
        state.log_call("memory_write", args, f"error: {error}")
        raise
    state.log_call("memory_write", args, result)
    return result


@server.tool()
def memory_str_replace(path: str, old_str: str, new_str: str, if_version: str) -> str:
    """Replace one exact occurrence of old_str in a memory file. old_str must occur exactly once;
    an empty new_str deletes the matched text. if_version is the file's current version token."""
    args = {"path": path, "old_str": old_str, "new_str": new_str, "if_version": if_version}
    try:
        _check_location(path)
        _check_version(path, if_version)
        content = _files()[path]["content"]
        count = content.count(old_str) if old_str else 0
        if count != 1:
            raise ValueError(f"claude-memory-stub: old_str occurs {count} times in {path}; it must occur exactly once")
        result = _store(path, content.replace(old_str, new_str, 1))
    except (ValueError, KeyError) as error:
        state.log_call("memory_str_replace", args, f"error: {error}")
        raise ValueError(str(error)) from error
    state.log_call("memory_str_replace", args, result)
    return result


@server.tool()
def memory_append(path: str, content: str, if_version: str) -> str:
    """Add text on a new line at the end of a memory file. if_version is the file's current version
    token, or "new" to create the file."""
    args = {"path": path, "content": content, "if_version": if_version}
    try:
        _check_location(path)
        _check_version(path, if_version)
        existing = _files().get(path, {}).get("content", "")
        joined = content if not existing else existing.rstrip("\n") + "\n" + content
        result = _store(path, joined)
    except ValueError as error:
        state.log_call("memory_append", args, f"error: {error}")
        raise
    state.log_call("memory_append", args, result)
    return result


@server.tool()
def memory_delete(path: str, if_version: str) -> str:
    """Remove a whole memory file. Needs the version token from a prior read."""
    args = {"path": path, "if_version": if_version}
    try:
        if if_version == "new":
            raise ValueError("claude-memory-stub: memory_delete needs the file's version token, not \"new\"")
        _check_version(path, if_version)
        del _files()[path]
        state.flush()
        result = f"Deleted {path}."  # UNVERIFIED wording
    except ValueError as error:
        state.log_call("memory_delete", args, f"error: {error}")
        raise
    state.log_call("memory_delete", args, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
