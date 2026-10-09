#!/usr/bin/env python3
"""Eval-only fake Gmail MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the subset of Gmail operations `triage`'s email workflow
(Step 7b) actually names: search_threads, get_thread, list_labels,
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
        "viewUrl": "<optional: overrides the generated URL; null omits it>",
        "messages": [{"id": "...", "from": "...", "to": [...],
                       "date": "...", "snippet": "...", "body": "...",
                       "viewUrl": "<optional, as for the thread>"}]
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

View URLs: the live Gmail MCP's tool descriptions say search_threads
"returns a list of threads, including their IDs, `viewUrl`, and related
messages (each with their own `viewUrl`)" and get_thread returns "its
`viewUrl` and a list of its messages (each with their own `viewUrl`)", and
its view and format enums list `view_url` "(if applicable)" in every one.
So search_threads gives each thread a "viewUrl", and get_thread gives the
thread and each of its messages one. The field name comes from those
descriptions; the URL format does not, because none is documented. The
stub's https://mail.google.com/mail/u/0/#all/<id> (the thread's or the
message's own id) is a plausible Gmail web address and a placeholder,
unverified against a live response. A thread or message whose fixture
entry sets "viewUrl" returns that value instead, and one that sets it to
null returns no viewUrl at all, for an eval about a thread with no link.
search_threads' listing carries no messages here (unlike the live tool's
related-message previews), so message URLs come only from get_thread.

Query support in search_threads is a small, documented subset of Gmail
syntax -- enough for triage's scoped-inbox flow and writing's corpus
searches: `in:inbox`, `in:sent`, `in:anywhere`, `from:<addr|me>`,
`to:<addr|me>`, `subject:<word>`, `label:<label_id>`, `is:unread`, bare
words (matched against subject+snippet), "quoted phrases", an uppercase
`OR` between two terms, and `-` negation of any of these.
Anything fancier matches nothing rather than silently matching everything,
and the raw query is always logged so a grader can see exactly what was
asked for. `from:` and `to:` match the thread-level participants, not each
individual message, so a fixture thread records the correspondent pair it
should be findable by.
"""

import copy
import datetime

from common import StubState

state = StubState(default={"threads": {}, "labels": {}, "drafts": {}})

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer("gmail-stub")


_VIEW_URL_BASE = "https://mail.google.com/mail/u/0/#all/"  # placeholder format; see View URLs above


def _with_view_url(view: dict, source: dict) -> dict:
    """Add the thread's or message's viewUrl: the fixture's own when it sets
    one, none when it sets null, otherwise the placeholder built from its id."""
    if "viewUrl" in source:
        url = source["viewUrl"]
    else:
        url = _VIEW_URL_BASE + source["id"]
    view.pop("viewUrl", None)
    if url is not None:
        view["viewUrl"] = url
    return view


def _thread_listing(t: dict) -> dict:
    """THREAD_VIEW_MINIMAL shape: no message bodies."""
    return _with_view_url({
        "id": t["id"],
        "snippet": t["snippet"],
        "subject": t["subject"],
        "from": t["from"],
        "to": t["to"],
        "date": t["date"],
        "labelIds": t["labelIds"],
    }, t)


def _resolve_address(addr: str) -> str:
    """`me` resolves to the fixture's account owner, as in real Gmail. A
    fixture that declares no owner resolves it to the empty string, which
    _term_matches treats as no match rather than as a match-everything
    substring."""
    if addr == "me":
        return str(state.data.get("me", "")).lower()
    return addr.lower()


def _in_matches(t: dict, place: str) -> bool:
    """`in:` names a location, which for this stub is a system label."""
    if place == "anywhere":
        return True
    return {"inbox": "INBOX", "sent": "SENT", "trash": "TRASH"}.get(place, "") in t["labelIds"]


# Operators this stub does not implement. Matching nothing keeps a fixture gap
# loudly visible in the log rather than silently matching everything.
#
# `after:`/`before:` are implemented (below) rather than listed here because
# the writing skill's whole caching design rests on one bounded "anything
# newer than my newest sample?" search. While those operators matched nothing,
# that search could never return a result, so no eval could exercise a cached
# card being extended -- the failure looked like "no new samples" every time.
# The relative forms (`newer_than:2d`) stay unimplemented; nothing needs them.
_UNIMPLEMENTED = ("is:", "has:", "category:",
                  "newer", "older", "size:", "larger:", "smaller:")


def _parse_query_date(arg: str):
    """Parse a Gmail date argument (2026/05/28, also tolerating 2026-05-28)."""
    try:
        return datetime.date(*(int(p) for p in arg.replace("-", "/").split("/")))
    except (TypeError, ValueError):
        return None


def _thread_date(t: dict):
    """The thread's date as a date object, or None if it is unparseable."""
    try:
        return datetime.date(*(int(p) for p in t["date"][:10].split("-")))
    except (KeyError, TypeError, ValueError):
        return None


def _date_matches(t: dict, arg: str, newer: bool) -> bool:
    """after:/before: -- strictly outside the named day, Gmail's own reading.

    An unparseable argument matches nothing, for the same reason an
    unimplemented operator does: a silent match-everything would turn a
    malformed query into a passing trial.
    """
    bound, actual = _parse_query_date(arg), _thread_date(t)
    if bound is None or actual is None:
        return False
    return actual > bound if newer else actual < bound

# Each entry maps an operator prefix to how its argument is tested.
_OPERATORS = {
    "in:": lambda t, arg: _in_matches(t, arg),
    "from:": lambda t, arg: bool(_resolve_address(arg)) and _resolve_address(arg) in t["from"].lower(),
    "to:": lambda t, arg: bool(_resolve_address(arg)) and any(
        _resolve_address(arg) in r.lower() for r in t["to"]),
    "subject:": lambda t, arg: arg.lower() in t["subject"].lower(),
    "label:": lambda t, arg: arg in t["labelIds"],
    "after:": lambda t, arg: _date_matches(t, arg, newer=True),
    "before:": lambda t, arg: _date_matches(t, arg, newer=False),
}


def _term_matches(t: dict, term: str) -> bool:
    if term == "is:unread":
        return "UNREAD" in t["labelIds"]
    if term == "is:read":
        return "UNREAD" not in t["labelIds"]
    if term == "is:starred":
        return "STARRED" in t["labelIds"]
    if term == "is:important":
        return "IMPORTANT" in t["labelIds"]
    for prefix, test in _OPERATORS.items():
        if term.startswith(prefix):
            return test(t, term[len(prefix):])
    if term.startswith(_UNIMPLEMENTED):
        return False
    lowered = term.lower()
    return lowered in t["subject"].lower() or lowered in t["snippet"].lower()


def _split_query(query: str) -> list:
    """Split on spaces, keeping a "quoted phrase" as one term."""
    terms, buffer, in_quotes = [], "", False
    for char in query:
        if char == '"':
            in_quotes = not in_quotes
            buffer += char
        elif char == " " and not in_quotes:
            if buffer:
                terms.append(buffer)
            buffer = ""
        else:
            buffer += char
    if buffer:
        terms.append(buffer)
    return terms


def _one_term_matches(t: dict, raw: str) -> bool:
    negated = raw.startswith("-")
    term = raw[1:] if negated else raw
    if len(term) > 1 and term.startswith('"') and term.endswith('"'):
        phrase = term.strip('"').lower()
        found = phrase in t["subject"].lower() or phrase in t["snippet"].lower()
    else:
        found = _term_matches(t, term)
    return found != negated


def _thread_matches(t: dict, query: str) -> bool:
    """Terms are AND-ed; an uppercase OR between two terms makes them one
    either-or term, as in Gmail (`from:a OR from:b`)."""
    # Parentheses only group an OR chain in practice, so they are dropped and
    # the chain is read as written.
    groups, terms = [], [term.strip("()") for term in _split_query(query) if term.strip("()")]
    index = 0
    while index < len(terms):
        group = [terms[index]]
        while index + 2 < len(terms) and terms[index + 1] == "OR":
            group.append(terms[index + 2])
            index += 2
        groups.append(group)
        index += 1
    return all(any(_one_term_matches(t, raw) for raw in group) for group in groups)


@server.tool()
def search_threads(
    query: str = "",
    pageSize: int = 20,
    pageToken: str = "",
    view: str = "THREAD_VIEW_MINIMAL",
    includeTrash: bool = False,
) -> dict:
    """Lists email threads, filtered by a Gmail-syntax query string. Returns
    listing-level fields only (no message bodies), including each thread's
    ID and `viewUrl` -- use get_thread for a full body. The stub supports
    a documented subset of query operators:
    in:inbox, in:sent, in:anywhere, from:, to:, subject:, label:<id>,
    is:unread, is:read, is:starred, is:important, bare words, "quoted
    phrases", OR between terms, and '-' negation. from:me and to:me resolve to the fixture's "me" address.
    Results come newest first."""
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
    """Retrieves one email thread, including its `viewUrl` and its messages
    (each with their own `viewUrl`). FULL_CONTENT (the
    default) includes each message's full body; MINIMAL and METADATA_ONLY
    progressively strip body and subject/snippet, mirroring the real tool."""
    if threadId not in state.data["threads"]:
        raise ValueError(f"gmail-stub: no thread with id {threadId!r}")
    t = state.data["threads"][threadId]
    messages = []
    for m in t["messages"]:
        msg = _with_view_url(dict(m), m)
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
