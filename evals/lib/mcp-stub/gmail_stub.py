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

Filters: a fixture that seeds a top-level "filters" list also gets
list_filters, create_filter, update_filter, and delete_filter, and the
server's instructions gain the sentence sift's own Gmail server
(sift_watch/gmail_mcp.py in dcwalker/sift) uses to say its filter tools
refuse forwarding and anything that keeps mail out of the inbox. Their
names, parameters, results, and refusals are copied from that server's
code, not guessed. Each filter is {"id", "criteria", "action"}, as the Gmail
API has it, with an action's "forward" an address. Who created a filter
makes no difference: any filter for one sender may gain labels in an edit,
and one matching more than one sender may only drop them. create_filter's evidence check counts the fixture threads from the
filter's sender (an address, or a domain and its subdomains) that are not
STARRED and carry every label it adds and none it removes; subject, query,
and the other narrowing criteria are not applied to that count. An update
creates a new filter ("filter_<n>") and deletes the old one, as sift's does,
since Gmail has no filter update.

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
    "view_url_style": "<optional: 'authuser' for the live format; see below>",
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
A live get_message and get_thread response (observed 2026-10-27) carried
https://mail.google.com/mail/?authuser=<the signed-in address>#all/<id>, so
a fixture that sets the top-level "view_url_style" to "authuser" gets that
form, with its "me" address, in place of the placeholder; the live id part
(thread-f:<number>) is not reproduced.
search_threads' listing carries no messages here (unlike the live tool's
related-message previews), so message URLs come only from get_thread.

Query support in search_threads is a small, documented subset of Gmail
syntax -- enough for triage's scoped-inbox flow, writing's corpus searches,
and sift-email's unprocessed-mail search: `in:inbox`, `in:sent`,
`in:anywhere`, `from:<addr|me>`, `to:<addr|me>`, `subject:<word>`,
`label:<name>`, `category:<tab>`, `is:unread`, `is:starred`,
`is:important`,
`after:`/`before:` (a date; epoch seconds match nothing),
`newer_than:`/`older_than:`, bare words (matched against subject+snippet),
"quoted phrases", an uppercase `OR` between two terms, and `-` negation of
any of these.

`label:` takes a label's display name, never its id, as the live connector's
search_threads description says ("Label IDs such as `Label_123` match
nothing"; checked live 2026-10-13: `label:Label_56` returned nothing and
`label:AI-Sifted` returned the threads). Quote a name with a space
(`label:"AI/Low priority"`) or write its spaces and `/` as `-`
(`label:AI-Low-priority`). Names compare without regard to letter case.

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
import re
from typing import Annotated

from pydantic import Field

from common import StubState

state = StubState(default={"threads": {}, "labels": {}, "drafts": {}})

from mcp.server.mcpserver import MCPServer  # noqa: E402

# Filter tools are served only to a fixture that seeds "filters" (see
# Filters below), so a trial of a skill or eval that has none sees the same
# tool list as before.
_FILTERS_SEEDED = "filters" in state.data
server = MCPServer(
    "gmail-stub",
    instructions=(
        "Filter tools list, create, update, and delete Gmail filters, and refuse forwarding and anything "
        "that keeps mail out of the inbox."
    ) if _FILTERS_SEEDED else None,
)


_VIEW_URL_BASE = "https://mail.google.com/mail/u/0/#all/"  # placeholder format; see View URLs above


def _with_view_url(view: dict, source: dict) -> dict:
    """Add the thread's or message's viewUrl: the fixture's own when it sets
    one, none when it sets null, otherwise one built from its id, in the live
    authuser form when the fixture asks for it."""
    if "viewUrl" in source:
        url = source["viewUrl"]
    elif state.data.get("view_url_style") == "authuser":
        url = f"https://mail.google.com/mail/?authuser={state.data.get('me', '')}#all/{source['id']}"
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
_UNIMPLEMENTED = ("is:", "has:",
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


def _label_form(name: str) -> str:
    """A label name as label: compares it: any letter case, with spaces and
    "/" read as "-", so "AI/Low priority" and AI-Low-priority are one name."""
    return name.strip('"').lower().replace(" ", "-").replace("/", "-")


def _label_matches(t: dict, arg: str) -> bool:
    """A label's display name, quoted or dashed. An id matches nothing."""
    wanted = _label_form(arg)
    ids = {l["id"] for l in state.data["labels"].values() if _label_form(l["name"]) == wanted}
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
    """after:/before: -- against midnight of the named day, as the live
    connector's description says: after: includes that day, before: excludes
    it (checked live 2026-10-26: after:2026/10/26 returned that day's mail).

    An all-digit argument (epoch seconds) matches nothing. A live search
    honored it on 2026-10-24, but by 2026-10-26 in:inbox after:<epoch>
    returned nothing even for an epoch a day and a half back, which left
    sift-email's routine finding no new mail for hours.

    An unparseable argument matches nothing, for the same reason an
    unimplemented operator does: a silent match-everything would turn a
    malformed query into a passing trial.
    """
    if arg.isdigit():
        return False
    bound, actual = _parse_query_date(arg), _thread_date(t)
    if bound is None or actual is None:
        return False
    return actual >= bound if newer else actual < bound

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
    "category:": lambda t, arg: _category_matches(t, arg),
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
            matches.append(t)
    matches = [_thread_listing(t) for t in sorted(matches, key=lambda t: t["date"], reverse=True)]
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
    labelId values with label_thread, unlabel_thread, and
    modify_thread_labels; search_threads' label: operator takes the name.
    Gmail's inbox tabs are listed too, as system labels: the five standard
    CATEGORY_* tabs, plus any further one a fixture's labels define."""
    labels = dict(state.data["labels"])
    for cid in sorted(_CATEGORY_IDS):
        labels.setdefault(cid, {"id": cid, "name": cid, "type": "system"})
    result = {"labels": [_label_view(l) for l in labels.values()]}
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


# Inbox tabs. The live label_thread description says adding the target
# CATEGORY_* label moves a thread to that tab (CATEGORY_PERSONAL for Primary)
# and "Gmail automatically removes the previous category", so a thread holds
# at most one. A fixture thread with none is in Primary.
_CATEGORY_IDS = {"CATEGORY_PERSONAL", "CATEGORY_SOCIAL", "CATEGORY_PROMOTIONS",
                 "CATEGORY_UPDATES", "CATEGORY_FORUMS"}
_CATEGORY_NAMES = {"primary": "CATEGORY_PERSONAL", "social": "CATEGORY_SOCIAL",
                   "promotions": "CATEGORY_PROMOTIONS", "updates": "CATEGORY_UPDATES",
                   "forums": "CATEGORY_FORUMS"}


def _category_matches(t: dict, arg: str) -> bool:
    """category:<tab> -- a thread with no category label counts as Primary."""
    wanted = _CATEGORY_NAMES.get(arg.lower())
    if wanted is None:
        return False
    held = [lbl for lbl in t["labelIds"] if lbl.startswith("CATEGORY_")]
    return wanted in held or (wanted == "CATEGORY_PERSONAL" and not held)


def _check_label_ids(label_ids: list[str]) -> None:
    system_ids = {"INBOX", "UNREAD", "STARRED", "IMPORTANT", "TRASH", "SPAM"} | _CATEGORY_IDS
    for lbl in label_ids:
        if lbl not in system_ids and lbl not in state.data["labels"]:
            raise ValueError(f"gmail-stub: no label with id {lbl!r} -- use list_labels for ids")


def _change_labels(t: dict, add: list[str], remove: list[str]) -> None:
    """Add and remove label ids on a thread, leaving every other label alone,
    except that adding a category replaces the thread's previous one."""
    if any(lbl.startswith("CATEGORY_") for lbl in add):
        t["labelIds"] = [lbl for lbl in t["labelIds"] if not lbl.startswith("CATEGORY_")]
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


# --- Filters (served only when the fixture seeds "filters"; see the docstring) ---

_FILTER_CRITERIA = {"from", "to", "subject", "query", "negatedQuery", "hasAttachment"}
# Copied from sift_watch/gmail_mcp.py: domains many unrelated senders share.
_SHARED_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "ymail.com", "outlook.com", "hotmail.com",
    "hotmail.co.uk", "live.com", "msn.com", "icloud.com", "me.com", "mac.com", "aol.com", "proton.me",
    "protonmail.com", "pm.me", "hey.com", "gmx.com", "gmx.net", "mail.com", "yandex.com", "zoho.com",
    "fastmail.com", "comcast.net", "att.net", "verizon.net", "sbcglobal.net",
    # Platforms that send on behalf of many unrelated senders.
    "substack.com", "googlegroups.com", "github.com", "amazonses.com", "sendgrid.net", "mailchimp.com",
    "mailchimpapp.net", "mcsv.net", "constantcontact.com", "groups.io", "facebookmail.com", "linkedin.com",
}
_SUFFIX_LABELS = {"co", "com", "org", "net", "gov", "ac", "edu", "ne", "or", "go", "gob", "nic", "ltd", "plc"}
_EVIDENCE_THREADS = 5
_SENDER_ADDRESS = re.compile(r"^[a-z0-9._%+'-]+@[a-z0-9-]+(\.[a-z0-9-]+)+$")
_SENDER_DOMAIN = re.compile(r"^@?([a-z0-9-]+(\.[a-z0-9-]+)+)$")
_WIDENING = re.compile(r"\bOR\b|[{}()]|\bfrom:", re.I)


def _user_only_actions(action: dict | None) -> list:
    action = action or {}
    adds = set(action.get("addLabelIds") or [])
    removes = set(action.get("removeLabelIds") or [])
    found = []
    if action.get("forward"):
        found.append("forwards")
    if "INBOX" in removes:
        found.append("skips the inbox")
    if "TRASH" in adds:
        found.append("deletes")
    if "SPAM" in adds:
        found.append("sends to Spam")
    if "SPAM" in removes:
        found.append("keeps mail out of Spam")
    return found


def _label_names() -> dict:
    return {lbl["id"]: lbl["name"] for lbl in state.data["labels"].values()}


def _filter_summary(f: dict) -> dict:
    names = _label_names()
    action = f.get("action") or {}
    return {
        "id": f["id"],
        "criteria": f.get("criteria") or {},
        "addLabels": [{"id": i, "name": names.get(i, i)} for i in action.get("addLabelIds") or []],
        "removeLabels": [{"id": i, "name": names.get(i, i)} for i in action.get("removeLabelIds") or []],
        "forwards": bool(action.get("forward")),
        "userOnly": _user_only_actions(action),
    }


def _find_filter(filter_id: str) -> dict:
    filter_id = str(filter_id or "").strip()
    if not filter_id:
        raise ValueError("filterId is empty")
    for f in state.data["filters"]:
        if f["id"] == filter_id:
            return f
    raise ValueError(f"Gmail API error 404: Filter not found: {filter_id}")


def _sender_problem(sender: str):
    domain = _SENDER_DOMAIN.match(sender)
    if not (_SENDER_ADDRESS.match(sender) or domain):
        return ("a filter sift creates needs `from` set to one sender's address or domain, "
                "such as news@example.com or example.com")
    account = str(state.data.get("me") or "").lower()
    own = account.rsplit("@", 1)[-1]
    if account and (sender == account or (domain and (domain.group(1) == own or domain.group(1).endswith("." + own)
                                                      or own.endswith("." + domain.group(1))))):
        return "a filter sift creates can't match the account's own mail or domain"
    if domain:
        name = domain.group(1)
        parts = name.split(".")
        shared = any(name == d or name.endswith("." + d) for d in _SHARED_DOMAINS)
        if shared or (len(parts) == 2 and parts[0] in _SUFFIX_LABELS):
            return f"{sender} is shared by many senders; name the sender's own address"
    return None


def _filter_criteria(criteria: dict) -> dict:
    criteria = {k: v for k, v in (criteria or {}).items() if v not in (None, "", False)}
    unknown = sorted(set(criteria) - _FILTER_CRITERIA)
    if unknown:
        raise ValueError(f"sift's filters can't use {', '.join(unknown)}")
    sender = str(criteria.get("from", "")).strip().lower()
    problem = _sender_problem(sender)
    if problem:
        raise ValueError(problem)
    criteria["from"] = sender
    for key in ("to", "subject", "query", "negatedQuery"):
        if key in criteria:
            criteria[key] = str(criteria[key]).strip()
            if _WIDENING.search(criteria[key]):
                raise ValueError(f"`{key}` may only narrow the sender's mail: no OR, parentheses, braces, or from:")
    return criteria


def _one_sender(criteria) -> bool:
    try:
        _filter_criteria(criteria)
    except ValueError:
        return False
    return True


def _normalized_ids(label_ids) -> list:
    system = {"INBOX", "UNREAD", "STARRED", "IMPORTANT", "TRASH", "SPAM"} | _CATEGORY_IDS
    out = []
    for raw in label_ids or []:
        lid = str(raw).strip()
        if lid.upper() in system:
            lid = lid.upper()
        if lid and lid not in out:
            out.append(lid)
    return out


def _check_label_ids(add: list, remove: list, old: dict) -> None:
    """Refuse a label sift may not add or remove, unless the filter being edited already had it."""
    old_add, old_remove = set(old.get("addLabelIds") or []), set(old.get("removeLabelIds") or [])
    for lid in add:
        if lid in old_add or lid == "IMPORTANT" or lid in _CATEGORY_IDS:
            continue
        if (state.data["labels"].get(lid) or {}).get("type") != "user":
            raise ValueError(f"sift's filters add user labels, IMPORTANT, or a CATEGORY_* tab, not {lid}")
    for lid in remove:
        if lid not in old_remove and lid != "IMPORTANT":
            raise ValueError(f"sift's filters only remove IMPORTANT, not {lid}")


def _filter_action(add_label_ids, remove_label_ids, old: dict | None = None) -> dict:
    add, remove = _normalized_ids(add_label_ids), _normalized_ids(remove_label_ids)
    if not add and not remove:
        raise ValueError("a filter needs labels to add or remove")
    if set(add) & set(remove):
        raise ValueError("a filter can't add and remove the same label")
    blocked = _user_only_actions({"addLabelIds": add, "removeLabelIds": remove})
    if blocked:
        raise ValueError(f"only the user sets a filter that {' or '.join(blocked)}")
    if len(set(add) & _CATEGORY_IDS) > 1:
        raise ValueError("a filter can put mail in one inbox tab at most")
    _check_label_ids(add, remove, old or {})
    action = {}
    if add:
        action["addLabelIds"] = add
    if remove:
        action["removeLabelIds"] = remove
    return action


def _from_sender(t: dict, sender: str) -> bool:
    raw = t.get("from", "")
    bracketed = re.search(r"<([^>]+)>", raw)
    address = (bracketed.group(1) if bracketed else raw).strip().lower()
    if "@" in sender:
        return address == sender
    domain = address.rsplit("@", 1)[-1]
    return domain == sender.lstrip("@") or domain.endswith("." + sender.lstrip("@"))


def _evidence(criteria: dict, action: dict) -> int:
    add, remove = set(action.get("addLabelIds") or []), set(action.get("removeLabelIds") or [])
    found = 0
    for t in state.data["threads"].values():
        labels = set(t["labelIds"])
        if _from_sender(t, criteria["from"]) and add <= labels and not remove & labels and "STARRED" not in labels:
            found += 1
    return found


def _new_filter_id() -> str:
    taken = {f["id"] for f in state.data["filters"]}
    n = len(taken) + 1
    while f"filter_{n}" in taken:
        n += 1
    return f"filter_{n}"


if _FILTERS_SEEDED:

    @server.tool()
    def list_filters() -> dict:
        """List the account's Gmail filters: each one's id, criteria, the labels it adds and removes (with names),
        whether it forwards (never where), and userOnly, what it does that only the user may change (forwarding,
        skipping the inbox, deleting, sending to Spam, or never sending to Spam)."""
        result = {"filters": [_filter_summary(f) for f in state.data["filters"]]}
        state.log_call("list_filters", {}, result)
        return result

    @server.tool()
    def create_filter(
        sender: Annotated[str, Field(description=(
            "The filter's `from`: one sender's address (news@example.com) or domain (example.com). Required; "
            "domains many senders share, such as gmail.com, are refused."))],
        addLabelIds: Annotated[list[str] | None, Field(description=(
            "Labels to add: user label IDs, IMPORTANT, or one CATEGORY_* tab."))] = None,
        removeLabelIds: Annotated[list[str] | None, Field(description="Labels to remove: only IMPORTANT.")] = None,
        to: Annotated[str, Field(description="Narrow to mail sent to this address.")] = "",
        subject: Annotated[str, Field(description="Narrow to subjects containing this phrase.")] = "",
        query: Annotated[str, Field(description="Narrow with a Gmail search.")] = "",
        negatedQuery: Annotated[str, Field(description="Leave out mail matching this Gmail search.")] = "",
        hasAttachment: Annotated[bool, Field(description="Narrow to mail with an attachment.")] = False,
    ) -> dict:
        """Create a Gmail filter for one sender's mail that adds or removes labels. It can't forward, skip the inbox,
        delete, or send to Spam, and needs 5 of the sender's unstarred threads already carrying every label it adds.
        Returns the new filter as list_filters shows it."""
        args = {"sender": sender, "addLabelIds": addLabelIds, "removeLabelIds": removeLabelIds, "to": to,
                "subject": subject, "query": query, "negatedQuery": negatedQuery, "hasAttachment": hasAttachment}
        try:
            criteria = _filter_criteria({"from": sender, "to": to, "subject": subject, "query": query,
                                         "negatedQuery": negatedQuery, "hasAttachment": hasAttachment})
            action = _filter_action(addLabelIds, removeLabelIds)
            found = _evidence(criteria, action)
            if found < _EVIDENCE_THREADS:
                raise ValueError(f"only {found} of {criteria['from']}'s unstarred threads carry these labels; "
                                 f"a filter needs {_EVIDENCE_THREADS}")
        except ValueError as error:
            state.log_call("create_filter", args, {"error": str(error)})
            raise
        created = {"id": _new_filter_id(), "criteria": criteria, "action": action}
        state.data["filters"].append(created)
        state.flush()
        result = _filter_summary(created)
        state.log_call("create_filter", args, result)
        return result

    @server.tool()
    def update_filter(
        filterId: Annotated[str, Field(description="The filter's id, from list_filters.")],
        addLabelIds: Annotated[list[str] | None, Field(description=(
            "Every label the filter should add from now on, replacing its current list."))] = None,
        removeLabelIds: Annotated[list[str] | None, Field(description=(
            "Every label the filter should remove from now on, replacing its current list."))] = None,
    ) -> dict:
        """Change the labels a filter adds or removes, keeping its criteria. Any of its current labels may be kept or
        dropped; new ones follow create_filter's rules, and only a filter for one sender may gain any.
        Refused for a filter with a userOnly action. Gmail can't edit a filter, so this creates the new one, then
        deletes the old: the result has the new id."""
        args = {"filterId": filterId, "addLabelIds": addLabelIds, "removeLabelIds": removeLabelIds}
        try:
            old = _find_filter(filterId)
            old_action = old.get("action") or {}
            blocked = _user_only_actions(old_action)
            if blocked:
                raise ValueError(f"this filter {' and '.join(blocked)}, so only the user changes it")
            action = _filter_action(addLabelIds, removeLabelIds, old_action)
            new = set(action.get("addLabelIds") or []) - set(old_action.get("addLabelIds") or [])
            new |= set(action.get("removeLabelIds") or []) - set(old_action.get("removeLabelIds") or [])
            if new and not _one_sender(old.get("criteria")):
                raise ValueError(f"this filter matches more than one sender, so an edit can only drop labels, "
                                 f"not add {', '.join(sorted(new))}")
            if all(set(action.get(k) or []) == set(old_action.get(k) or [])
                   for k in ("addLabelIds", "removeLabelIds")):
                raise ValueError("the filter already does exactly this")
        except ValueError as error:
            state.log_call("update_filter", args, {"error": str(error)})
            raise
        created = {"id": _new_filter_id(), "criteria": copy.deepcopy(old.get("criteria") or {}), "action": action}
        state.data["filters"] = [f for f in state.data["filters"] if f["id"] != old["id"]] + [created]
        state.flush()
        result = {"filter": _filter_summary(created), "replaced": old["id"]}
        state.log_call("update_filter", args, result)
        return result

    @server.tool()
    def delete_filter(
        filterId: Annotated[str, Field(description="The filter's id, from list_filters.")],
    ) -> dict:
        """Delete a filter. Refused for a filter with a userOnly action."""
        args = {"filterId": filterId}
        try:
            old = _find_filter(filterId)
            blocked = _user_only_actions(old.get("action"))
            if blocked:
                raise ValueError(f"this filter {' and '.join(blocked)}, so only the user deletes it")
        except ValueError as error:
            state.log_call("delete_filter", args, {"error": str(error)})
            raise
        state.data["filters"] = [f for f in state.data["filters"] if f["id"] != old["id"]]
        state.flush()
        result = {"deleted": old["id"]}
        state.log_call("delete_filter", args, result)
        return result


if __name__ == "__main__":
    server.run(transport="stdio")
