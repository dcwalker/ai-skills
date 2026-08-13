#!/usr/bin/env python3
"""Eval-only fake Slack MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the subset of Slack operations a corpus-building skill
actually calls: slack_search_public_and_private, slack_read_channel,
slack_read_thread, slack_search_users, slack_search_channels,
slack_read_user_profile, and slack_send_message. See common.py's module
docstring for the general stub-server design.

Schema fidelity note: every tool's parameters AND its response rendering
were copied from a live connected Slack MCP server, not guessed from
prose. That matters more here than for the other stubs in this directory,
because these tools do not return JSON objects -- they return
human-readable text inside a thin JSON envelope, with a different layout
per tool. A stub that returned tidy dicts would be easy to write, would
pass its own tests, and would measure nothing about how a skill copes with
the real thing.

The envelopes, verbatim from the live server:

  search_*          {"results": "<markdown>", "pagination_info": "..."}
  read_channel      {"messages": "<text>", "pagination_info": "..."}
  read_thread       {"messages": "<text>", "pagination_info": "..."}
  read_user_profile {"result": "<key: value lines>"}
  send_message      {"message_link": "...", "message_context": {...}}

Two details of the live rendering that a skill reading Slack has to cope
with, and which are therefore reproduced here: message text keeps Slack's
raw markup, so links appear as `<url|display>` and mentions as
`<@U123|display name>`, and channel reads are newest-first while thread
reads are oldest-first.

Unlike the Gmail stub, this one CAN write: slack_send_message appends to
the state. The real connector can post, so a trial where a skill posts
without being asked has to be a finding about the skill rather than
something the harness made impossible.

Environment: MCP_STUB_STATE_FILE / MCP_STUB_STATE_OUT / MCP_STUB_LOG, same
contract as trello_stub.py.

State model (the fake Slack workspace):
  {
    "me": {"id": "U...", "name": "...", "real_name": "...",
            "email": "...", "timezone": "...", "org": "..."},
    "users": {"<user_id>": {"id", "name", "real_name", "email",
                             "title", "timezone"}},
    "channels": {"<channel_id>": {"id": "C...", "name": "channel-name",
                                   "purpose": "...", "creator": "U...",
                                   "created": "<display time>",
                                   "is_archived": false,
                                   "type": "public_channel" | "im"}},
    "messages": {"<channel_id>": [{
        "ts": "1754382600.000100",     # Slack ts, also the sort key
        "time": "2026-08-05 09:30:00 PDT",   # rendered verbatim
        "user": "<user_id>",
        "text": "...",
        "thread_ts": null or "<parent ts>",
        "reactions": [{"name": "eyes", "count": 1}]
    }]}
  }

Times are stored as display strings rather than computed from `ts`, so a
fixture reads the way the live server's output reads and no timezone maths
can drift between runs.

Two deliberate divergences from the live server, both harmless to what
these evals measure and both worth knowing before trusting a diff: results
are ordered newest-first because the live default `sort="score"` is an
opaque relevance ranking, and messages posted through the API carry a
`*Sent using* <app>` line live, which a fixture of organically typed
messages has no reason to reproduce.

Query support in slack_search_public_and_private is a small, documented
subset of Slack's search syntax: `in:#channel-name`, `in:<#C123>`,
`from:<@U123>`, `from:username`, `is:thread`, `before:`/`after:`/`on:`
against the YYYY-MM-DD prefix of a message's display time, quoted "exact
phrases", bare words (AND-ed, matched against text), and `-` negation of
any of these. Anything else matches nothing rather than silently matching
everything, and the raw query is always logged so a grader can see exactly
what was asked for.
"""

import copy

from common import StubState

state = StubState(default={"me": {}, "users": {}, "channels": {}, "messages": {}})

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer("slack-stub")

_NO_MORE = "End of results - No more pages available.\\n"
_NOT_FOUND = "slack-stub: channel_not_found: "
_DETAILED = "detailed"
_SEARCH_HEADER = "# Search Results for: "
_PUBLIC = "public_channel"
_PAGINATION = "pagination_info"
_RESULT = "### Result "


def _search_body(query: str, section: str, rows: list) -> str:
    """The shared shape of every search response: a header, then either the
    no-results line or a `## <section> (N results)` block."""
    if not rows:
        return f"{_SEARCH_HEADER}{query}\n\nNo results found.\n"
    return (f"{_SEARCH_HEADER}{query}\n\n## {section} ({len(rows)} results)\n"
            + "".join(rows))


def _search_response(body: str) -> dict:
    return {"results": body, _PAGINATION: _NO_MORE}


def _read_response(body: str, note: str) -> dict:
    return {"messages": body, _PAGINATION: note}


def _user(user_id: str) -> dict:
    return state.data["users"].get(user_id, {"id": user_id, "name": "", "real_name": "", "email": ""})


def _require_channel(channel_id: str) -> dict:
    """Resolve a channel or raise the server's own not-found error."""
    channel = _channel(channel_id)
    if channel is None:
        raise ValueError(f"{_NOT_FOUND}{channel_id!r}")
    return channel


def _channel(channel_id: str) -> dict | None:
    """Channels are addressable by id or by name, as they are live."""
    channels = state.data["channels"]
    if channel_id in channels:
        return channels[channel_id]
    wanted = channel_id.lstrip("#").lower()
    for channel in channels.values():
        if channel["name"].lower() == wanted:
            return channel
    return None


def _sender(message: dict, with_id_label: bool = False) -> str:
    """`dan.walker <dan.walker@example.com> (U0BQ4B0TBA6)` in channel reads,
    and the same with an `ID: ` prefix in search results -- the live server
    labels the two differently."""
    user = _user(message["user"])
    uid = user.get("id", message["user"])
    return f"{user.get('real_name', '')} <{user.get('email', '')}> ({'ID: ' if with_id_label else ''}{uid})"


def _messages_in(channel_id: str) -> list:
    return state.data["messages"].get(channel_id, [])


def _is_thread_reply(message: dict) -> bool:
    """A reply lives in its thread, not in the channel timeline: the live
    server omits these from both channel history and ordinary search."""
    return bool(message.get("thread_ts")) and message["thread_ts"] != message["ts"]


def _reply_count(channel_id: str, ts: str) -> int:
    return sum(1 for m in _messages_in(channel_id) if m.get("thread_ts") == ts and m["ts"] != ts)


# --- search -----------------------------------------------------------------

def _term_matches(message: dict, channel: dict, term: str) -> bool:
    lowered = term.lower()
    if lowered.startswith("in:"):
        wanted = lowered[3:].strip("<>#").split("|")[0]
        return wanted in (channel["name"].lower(), channel["id"].lower())
    if lowered.startswith("from:"):
        wanted = lowered[5:].strip("<>@").split("|")[0]
        user = _user(message["user"])
        return wanted in (
            str(user.get("id", "")).lower(),
            str(user.get("name", "")).lower(),
            str(user.get("real_name", "")).lower(),
        )
    if lowered == "is:thread":
        return bool(message.get("thread_ts"))
    for prefix in ("before:", "after:", "on:"):
        if lowered.startswith(prefix):
            date, day = lowered[len(prefix):], message.get("time", "")[:10]
            if not day:
                return False
            return {"before:": day < date, "after:": day > date, "on:": day == date}[prefix]
    if lowered.startswith(("to:", "has:", "hasmy:", "creator:", "during:")):
        # Unimplemented operator: match nothing, loudly visible in the log,
        # rather than silently matching everything.
        return False
    return lowered.strip('"') in message["text"].lower()


def _split_terms(query: str) -> list:
    """Split on spaces, except inside a "quoted phrase"."""
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


def _matches(message: dict, channel: dict, query: str) -> bool:
    for term in _split_terms(query):
        negated = term.startswith("-")
        if _term_matches(message, channel, term[1:] if negated else term) == negated:
            return False
    return True


def _render_context(channel_id: str, message: dict, seen: set) -> str:
    """The live server lists neighbouring messages under Context before/after,
    collapsing any it already printed to `[See result above]`."""
    messages = sorted(_messages_in(channel_id), key=lambda m: m["ts"])
    index = next(i for i, m in enumerate(messages) if m["ts"] == message["ts"])
    out = ""
    for label, neighbours in (("Context before", messages[max(0, index - 3):index]),
                              ("Context after", messages[index + 1:index + 4])):
        if not neighbours:
            continue
        out += f"{label}: \n"
        for neighbour in neighbours:
            user = _user(neighbour["user"])
            head = f"From: {user.get('real_name', '')} <{user.get('email', '')}> (ID: {user.get('id', '')})"
            if neighbour["ts"] in seen:
                out += f"- [See result above] {head} Message_ts: {neighbour['ts']}\n"
            else:
                out += f"- {head} \n  Message_ts: {neighbour['ts']}\n  {neighbour['text']}\n"
    return out


def _render_hit(index: int, total: int, channel: dict, message: dict,
                seen: set, include_context: bool) -> str:
    """One `### Result i of N` block, laid out as the live server lays it out."""
    replies = _reply_count(channel["id"], message["ts"])
    permalink = (f"https://example.slack.com/archives/{channel['id']}"
                 f"/p{message['ts'].replace('.', '')}")
    if replies:
        permalink += f"?thread_ts={message['ts']}&cid={channel['id']}"
    out = (
        f"{_RESULT}{index} of {total}\n"
        f"Channel: #{channel['name']} (ID: {channel['id']})\n"
        f"From: {_sender(message, with_id_label=True)} \n"
        f"Time: {message.get('time', '')}\n"
        f"Message_ts: {message['ts']}\n"
    )
    if replies:
        out += f"Reply count: {replies}\n"
    out += f"Permalink: [link]({permalink})\nText: \n{message['text']}\n"
    if include_context:
        out += _render_context(channel["id"], message, seen)
    return out + "\n---\n\n"


def _render_hits(query: str, hits: list, include_context: bool) -> str:
    seen, rows = set(), []
    for index, (channel, message) in enumerate(hits, start=1):
        rows.append(_render_hit(index, len(hits), channel, message, seen, include_context))
        seen.add(message["ts"])
    return _search_body(query, "Messages", rows)


def _searchable(channel_id: str, query: str) -> list:
    """Messages in one channel that ordinary search can see. Thread replies
    live in their thread, so they surface only for an explicit is:thread."""
    wants_threads = "is:thread" in query.lower()
    return [m for m in _messages_in(channel_id)
            if wants_threads or not _is_thread_reply(m)]


def _collect_hits(query: str, limit: int, sort_dir: str) -> list:
    hits = []
    for channel_id in state.data["messages"]:
        channel = _channel(channel_id)
        if channel is None:
            continue
        hits += [(channel, m) for m in _searchable(channel_id, query)
                 if _matches(m, channel, query)]
    hits.sort(key=lambda pair: pair[1]["ts"], reverse=(sort_dir != "asc"))
    return hits[:min(limit, 20)]


@server.tool()
def slack_search_public_and_private(  # NOSONAR(S107) 15 params = the real tool's schema
    query: str,
    limit: int = 20,
    cursor: str = "",
    sort: str = "score",
    sort_dir: str = "desc",
    content_types: str = "messages",
    channel_types: str = "public_channel,private_channel,mpim,im",
    include_context: bool = True,
    include_bots: bool = False,
    only_my_channels: bool = False,
    max_context_length: int = 0,
    context_channel_id: str = "",
    response_format: str = _DETAILED,
    before: str = "",
    after: str = "",
) -> dict:
    """Searches for messages, files in ALL Slack channels, including public
    channels, private channels, DMs, and group DMs. Supports a documented
    subset of Slack search syntax: in:, from:, is:thread, before:/after:/on:,
    quoted phrases, bare words, and '-' negation."""
    hits = _collect_hits(query, limit, sort_dir)
    body = _render_hits(query, hits, include_context)

    result = _search_response(body)
    state.log_call("slack_search_public_and_private",
                   {"query": query, "limit": limit, "sort": sort,
                    "include_context": include_context}, result)
    return result


@server.tool()
def slack_read_channel(
    channel_id: str,
    limit: int = 100,
    cursor: str = "",
    oldest: str = "",
    latest: str = "",
    response_format: str = _DETAILED,
) -> dict:
    """Reads messages from a Slack channel in reverse chronological order
    (newest first). To read DM history, use a user_id as channel_id."""
    channel = _require_channel(channel_id)
    messages = sorted((m for m in _messages_in(channel["id"]) if not _is_thread_reply(m)),
                      key=lambda m: m["ts"], reverse=True)[:limit]

    body = f"Channel: #{channel['name']} ({channel['id']})\n"
    for message in messages:
        body += (
            f"\n=== Message from {_sender(message)} at {message.get('time', '')} === \n"
            f"Message TS: {message['ts']}\n"
            f"{message['text']}"
        )
        replies = _reply_count(channel["id"], message["ts"])
        if replies:
            latest_reply = max(m.get("time", "") for m in _messages_in(channel["id"])
                               if m.get("thread_ts") == message["ts"] and m["ts"] != message["ts"])
            body += f"\nThread: {replies} replies (latest: {latest_reply})"
        if message.get("reactions"):
            rendered = ", ".join(f"{r['name']} ({r['count']})" for r in message["reactions"])
            body += f"\nReactions: {rendered}"
        body += "\n"

    result = _read_response(body.rstrip("\n"), "There are no more messages available.\n")
    state.log_call("slack_read_channel",
                   {"channel_id": channel_id, "limit": limit}, result)
    return result


@server.tool()
def slack_read_thread(
    channel_id: str,
    message_ts: str,
    limit: int = 100,
    cursor: str = "",
    oldest: str = "",
    latest: str = "",
    response_format: str = _DETAILED,
) -> dict:
    """Reads messages from a specific Slack thread (parent message + all
    replies), oldest first."""
    channel = _require_channel(channel_id)
    messages = _messages_in(channel["id"])
    parent = next((m for m in messages if m["ts"] == message_ts), None)
    if parent is None:
        raise ValueError(f"slack-stub: no message with ts {message_ts!r} in {channel['name']}")
    replies = sorted((m for m in messages
                      if m.get("thread_ts") == message_ts and m["ts"] != message_ts),
                     key=lambda m: m["ts"])[:limit]

    def block(message: dict) -> str:
        user = _user(message["user"])
        return (
            f"From: {user.get('real_name', '')} <{user.get('email', '')}> ({user.get('id', '')})\n"
            f"Time: {message.get('time', '')}\n"
            f"Message TS: {message['ts']}\n"
            f"{message['text']}\n"
        )

    body = f"=== THREAD PARENT MESSAGE ===\n{block(parent)}\n"
    body += f"=== THREAD REPLIES ({len(replies)} total) ===\n"
    for index, reply in enumerate(replies, start=1):
        body += f"\n--- Reply {index} of {len(replies)} ---\n{block(reply)}"

    result = _read_response(body, "There are no more messages in this thread.\n")
    state.log_call("slack_read_thread",
                   {"channel_id": channel_id, "message_ts": message_ts}, result)
    return result


@server.tool()
def slack_search_users(query: str, limit: int = 20, cursor: str = "",
                       response_format: str = _DETAILED) -> dict:
    """Search for Slack users by name, email, or profile attributes."""
    terms = query.lower().split()
    hits = []
    for user in state.data["users"].values():
        haystack = " ".join(str(user.get(field, "")).lower()
                            for field in ("name", "real_name", "email", "title"))
        if all(term in haystack for term in terms if not term.startswith("-")) and \
           not any(term[1:] in haystack for term in terms if term.startswith("-")):
            hits.append(user)
    hits = hits[:min(limit, 20)]

    rows = []
    for index, user in enumerate(hits, start=1):
        rows.append(
            f"{_RESULT}{index} of {len(hits)}\n"
            f"Name: {user.get('real_name', '')}\n"
            f"User ID: {user.get('id', '')}\n"
            f"Title: {user.get('title', '')}\n"
            f"Email: {user.get('email', '')}\n"
            f"Timezone: {user.get('timezone', '')}\n"
            f"Profile Pic: [Photo](https://example.com/avatar/{user.get('id', '')}.jpg)\n"
            f"Permalink: [link](https://example.slack.com/team/{user.get('id', '')})\n"
            "\n---\n\n")
    result = _search_response(_search_body(query, "Users", rows))
    state.log_call("slack_search_users", {"query": query, "limit": limit}, result)
    return result


@server.tool()
def slack_search_channels(query: str, limit: int = 20, cursor: str = "",
                          channel_types: str = _PUBLIC,
                          include_archived: bool = False,
                          response_format: str = _DETAILED) -> dict:
    """Search for Slack channels by name or description."""
    lowered = query.lower()
    hits = [c for c in state.data["channels"].values()
            if c.get("type", _PUBLIC) != "im"
            and (lowered in c["name"].lower() or lowered in c.get("purpose", "").lower())
            and (include_archived or not c.get("is_archived"))][:min(limit, 20)]

    rows = []
    for index, channel in enumerate(hits, start=1):
        creator = _user(channel.get("creator", ""))
        rows.append(
            f"{_RESULT}{index} of {len(hits)}\n"
            f"Name: #{channel['name']}\n"
            f"Creator: {creator.get('real_name', '')} (<@{creator.get('id', '')})\n"
            f"Created: {channel.get('created', '')}\n"
            f"Purpose: {channel.get('purpose', '')}\n"
            f"Permalink: [link](https://example.slack.com/archives/{channel['id']})\n"
            f"Is Archived: {str(bool(channel.get('is_archived'))).lower()}\n"
            f"Channel Type: {channel.get('type', _PUBLIC)}\n"
            "\n---\n\n")
    result = _search_response(_search_body(query, "Channels", rows))
    state.log_call("slack_search_channels", {"query": query, "limit": limit}, result)
    return result


@server.tool()
def slack_read_user_profile(user_id: str = "", include_locale: bool = False,
                            response_format: str = _DETAILED) -> dict:
    """Retrieves detailed profile information for a Slack user. Defaults to
    the current user if user_id is not provided."""
    me = state.data.get("me", {})
    user = _user(user_id) if user_id else me
    is_me = not user_id or user.get("id") == me.get("id")
    body = (
        f"User ID: {user.get('id', '')}\n"
        f"Username: {user.get('name', '')}\n"
        f"Display Name: {user.get('display_name', '')}\n"
        f"Real Name: {user.get('real_name', '')}\n"
        f"Pronouns: \n"
        f"Title: {user.get('title', '')}\n"
        f"Email: {user.get('email', '')}\n"
        f"Organization Name: {me.get('org', '')}\n"
        f"Phone: \n"
        f"Status:  \n"
        f"Timezone: {user.get('timezone', '')}\n"
        f"Admin: {'Yes' if is_me else 'No'}\n"
        f"Owner: {'Yes' if is_me else 'No'}\n"
        "Bot: No\n"
        "Restricted: No\n"
    )
    result = {"result": body}
    state.log_call("slack_read_user_profile", {"user_id": user_id}, result)
    return result


@server.tool()
def slack_send_message(channel_id: str, message: str, thread_ts: str = "",
                       reply_broadcast: bool = False, draft_id: str = "",
                       unfurl_app_links: bool = False) -> dict:
    """Sends a message to a Slack channel or user. To DM a user, use their
    user_id as channel_id."""
    channel = _require_channel(channel_id)
    me = state.data.get("me", {})
    existing = state.data["messages"].setdefault(channel["id"], [])
    ts = f"{1800000000 + len(existing)}.000100"
    existing.append({
        "ts": ts,
        "time": "",
        "user": me.get("id", ""),
        "text": message,
        "thread_ts": thread_ts or None,
        "reactions": [],
    })
    state.flush()
    result = {
        "message_link": f"https://example.slack.com/archives/{channel['id']}/p{ts.replace('.', '')}",
        "message_context": {"message_ts": ts, "channel_id": channel["id"]},
    }
    state.log_call("slack_send_message",
                   {"channel_id": channel_id, "message": message,
                    "thread_ts": thread_ts}, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
