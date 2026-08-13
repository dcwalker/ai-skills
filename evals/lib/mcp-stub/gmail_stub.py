#!/usr/bin/env python3
"""Eval-only fake Gmail MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the subset of Gmail operations `triage`'s email workflow
(Step 4b) actually names: search_threads, get_thread, list_labels,
create_draft, modify_thread_labels, archive_thread. See common.py's module
docstring for the general stub-server design.

Schema fidelity note: in a real session these six tools span TWO connectors
-- the official Gmail MCP (search_threads / get_thread / list_labels /
create_draft, RPC-style camelCase parameters) and a helper connector
(modify_thread_labels / archive_thread, snake_case parameters). This stub
serves all six from one server for trial simplicity, but each tool's
parameter names and shapes were copied from the live connected servers, not
guessed, so a skill's real calls match instead of silently no-oping.

Like the real Gmail MCP, this stub CANNOT send email: create_draft only
stores a draft. There is deliberately no send tool, so an eval can assert
sending stayed with the user simply because no such call is possible.

Environment: MCP_STUB_STATE_FILE / MCP_STUB_STATE_OUT / MCP_STUB_LOG, same
contract as trello_stub.py.

State model (the fake Gmail "database"):
  {
    "threads": {"<thread_id>": {
        "id": "...",
        "subject": "...",
        "from": "sender@example.com",
        "to": ["user@example.com"],
        "date": "<ISO datetime>",
        "snippet": "...",
        "labelIds": ["INBOX", "UNREAD", "Label_7", ...],
        "messages": [{"id": "...", "from": "...", "to": [...],
                       "date": "...", "snippet": "...", "body": "..."}]
    }},
    "labels": {"<label_id>": {"id": "...", "name": "...",
                               "type": "system" or "user"}},
    "drafts": {"<draft_id>": {"id": "...", "to": [...], "cc": [...],
                               "bcc": [...], "subject": "...", "body": "...",
                               "replyToMessageId": null or "<message_id>"}},
    "me": "user@example.com"
  }

The optional top-level "me" is the fixture's account owner, and it is what
`from:me` / `to:me` resolve to, as they do in real Gmail. A fixture that
omits it makes those two terms match nothing (see below).

Query support in search_threads is a small, documented subset of Gmail
syntax -- enough for triage's scoped-inbox flow and writing's corpus
searches: `in:inbox`, `in:sent`, `in:anywhere`, `from:<addr|me>`,
`to:<addr|me>`, `subject:<word>`, `label:<label_id>`, `is:unread`, bare
words (matched against subject+snippet), and `-` negation of any of these.
Anything fancier matches nothing rather than silently matching everything,
and the raw query is always logged so a grader can see exactly what was
asked for. `from:` and `to:` match the thread-level participants, not each
individual message, so a fixture thread records the correspondent pair it
should be findable by.
"""

import copy

from common import StubState

state = StubState(default={"threads": {}, "labels": {}, "drafts": {}})

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer("gmail-stub")


def _thread_listing(t: dict) -> dict:
    """THREAD_VIEW_MINIMAL shape: no message bodies."""
    return {
        "id": t["id"],
        "snippet": t["snippet"],
        "subject": t["subject"],
        "from": t["from"],
        "to": t["to"],
        "date": t["date"],
        "labelIds": t["labelIds"],
    }


def _resolve_address(addr: str) -> str:
    """`me` resolves to the fixture's account owner, as in real Gmail. A
    fixture that declares no owner resolves it to the empty string, which
    _term_matches treats as no match rather than as a match-everything
    substring."""
    if addr == "me":
        return str(state.data.get("me", "")).lower()
    return addr.lower()


def _term_matches(t: dict, term: str) -> bool:
    if term.startswith("in:"):
        place = term[3:]
        if place == "anywhere":
            return True
        if place == "inbox":
            return "INBOX" in t["labelIds"]
        if place == "sent":
            return "SENT" in t["labelIds"]
        if place == "trash":
            return "TRASH" in t["labelIds"]
        return False
    if term.startswith("from:"):
        addr = _resolve_address(term[5:])
        return bool(addr) and addr in t["from"].lower()
    if term.startswith("to:"):
        addr = _resolve_address(term[3:])
        return bool(addr) and any(addr in r.lower() for r in t["to"])
    if term.startswith("subject:"):
        return term[8:].lower() in t["subject"].lower()
    if term.startswith("label:"):
        return term[6:] in t["labelIds"]
    if term == "is:unread":
        return "UNREAD" in t["labelIds"]
    if term == "is:read":
        return "UNREAD" not in t["labelIds"]
    if term.startswith(("is:", "has:", "category:", "after:", "before:",
                        "newer", "older", "size:", "larger:", "smaller:")):
        # Unimplemented operator: match nothing, loudly visible in the log,
        # rather than silently matching everything.
        return False
    return term.lower() in t["subject"].lower() or term.lower() in t["snippet"].lower()


def _thread_matches(t: dict, query: str) -> bool:
    for raw in query.split():
        if raw.startswith("-"):
            if _term_matches(t, raw[1:]):
                return False
        elif not _term_matches(t, raw):
            return False
    return True


@server.tool()
def search_threads(
    query: str = "",
    pageSize: int = 20,
    pageToken: str = "",
    view: str = "THREAD_VIEW_MINIMAL",
    includeTrash: bool = False,
) -> dict:
    """Lists email threads, filtered by a Gmail-syntax query string. Returns
    listing-level fields only (no message bodies) -- use get_thread for a
    full body. The stub supports a documented subset of query operators:
    in:inbox, in:sent, in:anywhere, from:, to:, subject:, label:<id>,
    is:unread, bare words, and '-' negation. from:me and to:me resolve to
    the fixture's "me" address."""
    matches = []
    for t in state.data["threads"].values():
        if not includeTrash and "TRASH" in t["labelIds"] and "in:trash" not in query and "in:anywhere" not in query:
            continue
        if not query or _thread_matches(t, query):
            matches.append(_thread_listing(t))
    matches.sort(key=lambda m: m["date"], reverse=True)
    result = {"threads": matches[:pageSize]}
    state.log_call(
        "search_threads",
        {"query": query, "pageSize": pageSize, "view": view, "includeTrash": includeTrash},
        result,
    )
    return result


@server.tool()
def get_thread(threadId: str, messageFormat: str = "FULL_CONTENT") -> dict:
    """Retrieves one email thread including its messages. FULL_CONTENT (the
    default) includes each message's full body; MINIMAL and METADATA_ONLY
    progressively strip body and subject/snippet, mirroring the real tool."""
    if threadId not in state.data["threads"]:
        raise ValueError(f"gmail-stub: no thread with id {threadId!r}")
    t = state.data["threads"][threadId]
    messages = []
    for m in t["messages"]:
        msg = dict(m)
        if messageFormat == "MINIMAL":
            msg.pop("body", None)
        elif messageFormat == "METADATA_ONLY":
            msg.pop("body", None)
            msg.pop("snippet", None)
        messages.append(msg)
    result = dict(_thread_listing(t), messages=messages)
    state.log_call("get_thread", {"threadId": threadId, "messageFormat": messageFormat}, result)
    return result


@server.tool()
def list_labels(pageSize: int = 0, pageToken: str = "") -> dict:
    """Lists all labels in the account, with each label's id, name, and
    type (system or user). Use the returned ids with modify_thread_labels
    and search_threads' label: operator."""
    result = {"labels": list(state.data["labels"].values())}
    state.log_call("list_labels", {}, result)
    return result


@server.tool()
def create_draft(
    to: list[str] | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    subject: str = "",
    body: str = "",
    htmlBody: str = "",
    replyToMessageId: str = "",
) -> dict:
    """Creates a new draft email and returns its id. The draft is saved,
    never sent -- the stub (like the real Gmail MCP) has no send operation;
    sending stays with the user."""
    if replyToMessageId:
        known = {m["id"] for t in state.data["threads"].values() for m in t["messages"]}
        if replyToMessageId not in known:
            raise ValueError(f"gmail-stub: no message with id {replyToMessageId!r}")
    new_id = f"draft-{len(state.data['drafts']) + 1}"
    draft = {
        "id": new_id,
        "to": to or [],
        "cc": cc or [],
        "bcc": bcc or [],
        "subject": subject,
        "body": body or htmlBody,
        "replyToMessageId": replyToMessageId or None,
    }
    state.data["drafts"][new_id] = draft
    state.flush()
    result = {"id": new_id}
    state.log_call("create_draft", copy.deepcopy(draft), result)
    return result


@server.tool()
def modify_thread_labels(
    thread_id: str,
    add_label_ids: list[str] | None = None,
    remove_label_ids: list[str] | None = None,
) -> dict:
    """Add or remove specific Gmail label IDs on a thread. Only the listed
    label IDs are affected; all unlisted labels remain unchanged. User label
    ids must already exist (see list_labels)."""
    if thread_id not in state.data["threads"]:
        raise ValueError(f"gmail-stub: no thread with id {thread_id!r}")
    system_ids = {"INBOX", "UNREAD", "STARRED", "IMPORTANT", "TRASH", "SPAM"}
    for lbl in add_label_ids or []:
        if lbl not in system_ids and lbl not in state.data["labels"]:
            raise ValueError(f"gmail-stub: no label with id {lbl!r} -- use list_labels for ids")
    t = state.data["threads"][thread_id]
    for lbl in add_label_ids or []:
        if lbl not in t["labelIds"]:
            t["labelIds"].append(lbl)
    for lbl in remove_label_ids or []:
        if lbl in t["labelIds"]:
            t["labelIds"].remove(lbl)
    state.flush()
    result = {"thread_id": thread_id, "labelIds": list(t["labelIds"])}
    state.log_call(
        "modify_thread_labels",
        {"thread_id": thread_id, "add_label_ids": add_label_ids, "remove_label_ids": remove_label_ids},
        result,
    )
    return result


@server.tool()
def archive_thread(thread_id: str) -> dict:
    """Archive a Gmail thread by removing it from the Inbox. Only the INBOX
    label is removed; all other labels stay intact and the thread remains
    searchable via in:anywhere."""
    if thread_id not in state.data["threads"]:
        raise ValueError(f"gmail-stub: no thread with id {thread_id!r}")
    t = state.data["threads"][thread_id]
    if "INBOX" in t["labelIds"]:
        t["labelIds"].remove("INBOX")
    state.flush()
    result = {"thread_id": thread_id, "labelIds": list(t["labelIds"])}
    state.log_call("archive_thread", {"thread_id": thread_id}, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
