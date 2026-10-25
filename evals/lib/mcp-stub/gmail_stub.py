#!/usr/bin/env python3
"""Eval-only fake Gmail MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the subset of Gmail operations `triage`'s email workflow
(Step 7b) actually names: search_threads, get_thread, list_labels,
create_draft, modify_thread_labels, archive_thread -- plus trash_thread and
create_label, which the workflow's delete branch and label bootstrap need
and which the official Gmail MCP offers -- and label_thread and
unlabel_thread, which `sift-email` labels with through the official
connector rather than the helper's modify_thread_labels. See common.py's
module docstring for the general stub-server design.

Schema fidelity note: in a real session these tools span TWO connectors
-- the official Gmail MCP (search_threads / get_thread / list_labels /
create_draft / trash_thread / create_label, RPC-style camelCase parameters)
and a helper connector (modify_thread_labels / archive_thread, snake_case
parameters). This stub serves all of them from one server for trial
simplicity, but each tool's
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
    "me": "user@example.com",
    "stub_now": "<ISO datetime, optional: the stub's fixed 'now'>"
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
syntax -- enough for triage's scoped-inbox flow, writing's corpus searches,
and sift-email's unprocessed-mail search: `in:inbox`, `in:sent`,
`in:anywhere`, `from:<addr|me>`, `to:<addr|me>`, `subject:<word>`,
`label:<label_id|name>`, `is:unread`, `is:starred`, `is:important`,
`after:`/`before:` (a date, or epoch seconds),
`newer_than:`/`older_than:`, bare words (matched against subject+snippet),
"quoted phrases", an uppercase `OR` between two terms, and `-` negation of
any of these.

`label:` takes a label id, which is the only form the live connector's
search_threads description documents. A display name, quoted when it holds
a space (`label:"AI/Low priority"`), matches too, because a live read-only
search with a quoted nested label name returned that label's threads
(2026-10-10). Names compare without regard to letter case.

`newer_than:`/`older_than:` take a number and a unit (d, m, or y; a month
counts as 30 days and a year as 365) and count back from the fixture's
optional top-level "stub_now", which fixture-dates.py moves with the rest of
the state, or from the real time without one. A fixture whose threads are
found by age should set "stub_now", or the same trial finds different
threads depending on the day it runs.
Anything fancier matches nothing rather than silently matching everything,
and the raw query is always logged so a grader can see exactly what was
asked for. `from:` and `to:` match the thread-level participants, not each
individual message, so a fixture thread records the correspondent pair it
should be findable by.
"""

import copy
import datetime
from typing import Annotated

from pydantic import Field

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
                  "newer:", "older:", "size:", "larger:", "smaller:")

_AGE_UNITS = {"d": 1, "m": 30, "y": 365}


def _stub_now() -> datetime.datetime:
    now = state.data.get("stub_now")
    if now:
        return datetime.datetime.fromisoformat(now.replace("Z", "+00:00"))
    return datetime.datetime.now(datetime.timezone.utc)


def _thread_datetime(t: dict):
    """The thread's date as an aware datetime (UTC when it names no zone),
    or None if it is unparseable."""
    try:
        moment = datetime.datetime.fromisoformat(t["date"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError, AttributeError):
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=datetime.timezone.utc)
    return moment


def _age_matches(t: dict, arg: str, newer: bool) -> bool:
    """newer_than:/older_than: -- relative to stub_now. A malformed argument
    matches nothing, like an unparseable after:/before: date."""
    if len(arg) < 2 or not arg[:-1].isdigit() or arg[-1].lower() not in _AGE_UNITS:
        return False
    actual = _thread_datetime(t)
    if actual is None:
        return False
    cutoff = _stub_now() - datetime.timedelta(days=int(arg[:-1]) * _AGE_UNITS[arg[-1].lower()])
    return actual > cutoff if newer else actual < cutoff


def _label_matches(t: dict, arg: str) -> bool:
    """A label id, or a label's display name in any letter case."""
    wanted = arg.strip('"')
    if wanted in t["labelIds"]:
        return True
    ids = {l["id"] for l in state.data["labels"].values() if l["name"].lower() == wanted.lower()}
    return any(i in t["labelIds"] for i in ids)


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
    An all-digit argument is epoch seconds, which the Gmail API's filtering
    guide documents and a live read-only search honored (2026-10-24), and is
    compared against the thread's full timestamp.

    An unparseable argument matches nothing, for the same reason an
    unimplemented operator does: a silent match-everything would turn a
    malformed query into a passing trial.
    """
    if arg.isdigit():
        moment = _thread_datetime(t)
        if moment is None:
            return False
        bound = datetime.datetime.fromtimestamp(int(arg), datetime.timezone.utc)
        return moment > bound if newer else moment < bound
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
    "label:": _label_matches,
    "newer_than:": lambda t, arg: _age_matches(t, arg, newer=True),
    "older_than:": lambda t, arg: _age_matches(t, arg, newer=False),
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
    in:inbox, in:sent, in:anywhere, from:, to:, subject:, label:<id or
    name>, after:, before:, newer_than:, older_than:, is:unread, is:read,
    is:starred, is:important, bare words, "quoted phrases", OR between
    terms, and '-' negation. from:me and to:me resolve to the fixture's "me" address.
    Results come newest first, at most 50 per page (20 by default). When more
    remain, the response carries a nextPageToken: pass it as pageToken to get
    the next page."""
    matches = []
    for t in state.data["threads"].values():
        if not includeTrash and "TRASH" in t["labelIds"] and "in:trash" not in query and "in:anywhere" not in query:
            continue
        if not query or _thread_matches(t, query):
            matches.append(_thread_listing(t))
    matches.sort(key=lambda m: m["date"], reverse=True)
    # Paging as the live tool does: pageSize defaults to 20 and is capped at
    # 50, and a page with more after it carries nextPageToken and
    # resultCountEstimate (both seen in a live response, 2026-10-10). The
    # token here is the next offset as a string, opaque to the caller.
    size = min(max(pageSize or 20, 1), 50)
    try:
        start = int(pageToken) if pageToken else 0
    except ValueError:
        raise ValueError(f"gmail-stub: invalid pageToken {pageToken!r}") from None
    result = {"threads": matches[start:start + size]}
    if start + size < len(matches):
        result["nextPageToken"] = str(start + size)
        result["resultCountEstimate"] = str(len(matches))
    state.log_call(
        "search_threads",
        {"query": query, "pageSize": pageSize, "pageToken": pageToken, "view": view,
         "includeTrash": includeTrash},
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


def _label_view(label: dict) -> dict:
    """A label as the live list_labels returns one (2026-10-10): labelId,
    name, labelType in upper case, the two visibilities when set, and
    message and thread counts, which the stub counts from its threads. The
    fixture keeps its own {id, name, type} shape."""
    threads = [t for t in state.data["threads"].values() if label["id"] in t["labelIds"]]
    messages = [m for t in threads for m in t.get("messages", [])]
    view = {"labelId": label["id"], "name": label["name"],
            "labelType": str(label.get("type", "user")).upper()}
    for key in ("labelListVisibility", "messageListVisibility"):
        if key in label:
            view[key] = label[key]
    view.update({
        "messagesTotal": len(messages),
        "messagesUnread": sum(1 for t in threads if "UNREAD" in t["labelIds"] for _ in t.get("messages", [])),
        "threadsTotal": len(threads),
        "threadsUnread": sum(1 for t in threads if "UNREAD" in t["labelIds"]),
    })
    return view


@server.tool()
def list_labels(pageSize: int = 0, pageToken: str = "") -> dict:
    """Lists all labels in the account. Each carries its labelId, name,
    labelType (SYSTEM or USER), and message and thread counts. Use the
    labelId values with label_thread, unlabel_thread, modify_thread_labels,
    and search_threads' label: operator."""
    result = {"labels": [_label_view(l) for l in state.data["labels"].values()]}
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
    if not add_label_ids and not remove_label_ids:
        # A call whose label lists were misnamed reaches here with neither,
        # and answering success would hide that nothing changed.
        raise ValueError("gmail-stub: give add_label_ids or remove_label_ids (label ids to add or remove)")
    _check_label_ids(add_label_ids or [])
    t = state.data["threads"][thread_id]
    _change_labels(t, add_label_ids or [], remove_label_ids or [])
    state.flush()
    result = {"thread_id": thread_id, "labelIds": list(t["labelIds"])}
    state.log_call(
        "modify_thread_labels",
        {"thread_id": thread_id, "add_label_ids": add_label_ids, "remove_label_ids": remove_label_ids},
        result,
    )
    return result


def _check_label_ids(label_ids: list[str]) -> None:
    system_ids = {"INBOX", "UNREAD", "STARRED", "IMPORTANT", "TRASH", "SPAM"}
    for lbl in label_ids:
        if lbl not in system_ids and lbl not in state.data["labels"]:
            raise ValueError(f"gmail-stub: no label with id {lbl!r} -- use list_labels for ids")


def _change_labels(t: dict, add: list[str], remove: list[str]) -> None:
    """Add and remove label ids on a thread, leaving every other label alone."""
    for lbl in add:
        if lbl not in t["labelIds"]:
            t["labelIds"].append(lbl)
    for lbl in remove:
        if lbl in t["labelIds"]:
            t["labelIds"].remove(lbl)


# The official connector's parameter names are camelCase. A validation alias
# publishes those names in the tool's schema and accepts only them, while the
# Python parameters stay snake_case.
ThreadIdArg = Annotated[str, Field(validation_alias="threadId")]
LabelIdsArg = Annotated[list[str], Field(validation_alias="labelIds")]


@server.tool()
def label_thread(thread_id: ThreadIdArg, label_ids: LabelIdsArg) -> dict:
    """Adds labels to an entire thread. Mirrors the official Gmail MCP's
    label_thread: label ids, not names (see list_labels), and an empty
    object back on success, as a live call returned (2026-10-10)."""
    if thread_id not in state.data["threads"]:
        raise ValueError(f"gmail-stub: no thread with id {thread_id!r}")
    _check_label_ids(label_ids)
    _change_labels(state.data["threads"][thread_id], label_ids, [])
    state.flush()
    result = {}
    state.log_call("label_thread", {"threadId": thread_id, "labelIds": label_ids}, result)
    return result


@server.tool()
def unlabel_thread(thread_id: ThreadIdArg, label_ids: LabelIdsArg) -> dict:
    """Removes labels from an entire thread. Mirrors the official Gmail
    MCP's unlabel_thread: label ids, and an empty object back on success.
    A listed label the thread does not carry is left alone."""
    if thread_id not in state.data["threads"]:
        raise ValueError(f"gmail-stub: no thread with id {thread_id!r}")
    _check_label_ids(label_ids)
    _change_labels(state.data["threads"][thread_id], [], label_ids)
    state.flush()
    result = {}
    state.log_call("unlabel_thread", {"threadId": thread_id, "labelIds": label_ids}, result)
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


@server.tool()
def trash_thread(threadId: str) -> dict:
    """Moves an entire thread to the Trash. Mirrors the official Gmail MCP's
    trash_thread (parameter name copied from its schema): the thread gains
    the TRASH system label and leaves the inbox."""
    if threadId not in state.data["threads"]:
        raise ValueError(f"gmail-stub: no thread with id {threadId!r}")
    t = state.data["threads"][threadId]
    if "INBOX" in t["labelIds"]:
        t["labelIds"].remove("INBOX")
    if "TRASH" not in t["labelIds"]:
        t["labelIds"].append("TRASH")
    state.flush()
    result = {"id": threadId, "labelIds": list(t["labelIds"])}
    state.log_call("trash_thread", {"threadId": threadId}, result)
    return result


@server.tool()
def create_label(
    displayName: str,
    autoCreateParentLabels: bool = True,
    colorPreset: str = "",
    labelListVisibility: str = "",
    messageListVisibility: str = "",
) -> dict:
    """Creates a new user label and returns it. Mirrors the official Gmail
    MCP's create_label (parameter names copied from its schema; the
    deprecated `color` field is omitted). Nested names ('A/B') create their
    missing parents when autoCreateParentLabels is true. A name that already
    exists, in any letter case, is an error, as in Gmail."""
    labels = state.data["labels"]
    names = {l["name"].lower(): l for l in labels.values()}
    if displayName.lower() in names:
        raise ValueError(f"gmail-stub: a label named {displayName!r} already exists")
    wanted = [displayName]
    if autoCreateParentLabels and "/" in displayName:
        parts = displayName.split("/")
        wanted = ["/".join(parts[:i]) for i in range(1, len(parts) + 1)]
    created = None
    for name in wanted:
        if name.lower() in names:
            continue
        new_id = f"Label_{len(labels) + 1}"
        while new_id in labels:
            new_id = f"Label_{int(new_id.split('_')[1]) + 1}"
        created = {"id": new_id, "name": name, "type": "user"}
        if labelListVisibility:
            created["labelListVisibility"] = labelListVisibility
        if messageListVisibility:
            created["messageListVisibility"] = messageListVisibility
        labels[new_id] = created
        names[name.lower()] = created
    state.flush()
    # The live create_label returned the new label as color, labelId, the
    # two visibilities (defaulting to LABEL_SHOW and SHOW), and name.
    result = {"color": {}, "labelId": created["id"],
              "labelListVisibility": created.get("labelListVisibility", "LABEL_SHOW"),
              "messageListVisibility": created.get("messageListVisibility", "SHOW"),
              "name": created["name"]}
    state.log_call("create_label", {"displayName": displayName,
                                    "autoCreateParentLabels": autoCreateParentLabels,
                                    "colorPreset": colorPreset,
                                    "labelListVisibility": labelListVisibility,
                                    "messageListVisibility": messageListVisibility}, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
