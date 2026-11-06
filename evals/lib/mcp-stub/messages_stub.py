#!/usr/bin/env python3
"""Eval-only fake text-messages MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the read tools of the "Read and Send iMessages" connector
that a meeting-notes skill uses to read text messages as a chat source:
read_imessages, get_unread_imessages, and search_contacts. The connector's
send tool is left out on purpose: no skill in this repo sends a text, and a
stub that cannot send makes "nothing was sent" hold by construction. See
common.py's module docstring for the general stub-server design.

Schema fidelity: tool names, descriptions, parameter names, types, defaults,
and parameter descriptions were copied from the live connector's schemas,
not guessed. The live tools were not called, so every response layout below
is designed, not copied, and flagged UNVERIFIED where it is built:

- read_imessages: a "Found N message(s) with <number> (most recent first):"
  line, then one line per message, newest first, as
  "[YYYY-MM-DD HH:MM:SS] <sender>: <text>". The sender is "Me" for the
  user's own messages and the thread's phone number otherwise; the stub
  does not resolve names, so a skill learns who a number is from
  search_contacts or a contacts source. Timestamps are the user's local
  wall-clock time with no offset shown.
- get_unread_imessages: the same line layout across every thread, newest
  first, under a "Found N unread message(s):" line. Reading leaves a
  message unread (the stub never changes state), which may differ live.
- search_contacts: a "Found N contact(s):" line, then each match as
  "Name:", "Phone:", and "Email:" lines, a blank line between two people.
- The wording when nothing matches, and how a phone number is matched:
  the stub compares digits only, using the last ten when both sides have
  at least ten, so "+1 (206) 555-0142", "206-555-0142", and "+12065550142"
  all name one thread.

State model (the fake message store):
  {
    "contacts": [
      {"name": "Marcus Hall",
       "phones": ["+12065550142"],
       "emails": ["marcus.hall@example.com"]}
    ],
    "threads": {
      "+12065550142": [
        {"timestamp": "2026-11-04T11:09:30-08:00",
         "from_me": false,
         "text": "quote came back at $18,400",
         "unread": false}
      ]
    }
  }

"emails" and "unread" are optional (unread defaults to false). Each thread
is keyed by the other person's number; its messages may be in any order,
since every response sorts them newest first. "timestamp" is an ISO
datetime with an offset, so fixture-dates.py moves it like any other date;
it is rendered at the offset it carries. search_contacts matches the query,
in any letter case, as a substring of a contact's name or emails, or, when
the query holds digits, against the digits of a contact's phones, which
are the three things the live description says it searches by ("name,
phone, or email").

Environment: MCP_STUB_STATE_FILE / MCP_STUB_STATE_OUT / MCP_STUB_LOG, same
contract as trello_stub.py.
"""

import datetime
import re
from typing import Annotated

from common import StubState

state = StubState(default={"contacts": [], "threads": {}})

from mcp.server.mcpserver import MCPServer  # noqa: E402
from pydantic import Field  # noqa: E402

server = MCPServer("messages-stub")


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _same_number(a: str, b: str) -> bool:
    """UNVERIFIED matching rule: digits only, the last ten when both sides
    have at least ten, so a country code is optional."""
    da, db = _digits(a), _digits(b)
    if not da or not db:
        return False
    if len(da) >= 10 and len(db) >= 10:
        return da[-10:] == db[-10:]
    return da == db


def _limit(limit: float) -> int:
    if limit != int(limit) or limit < 1:
        raise ValueError("messages-stub: limit must be a positive whole number")
    return int(limit)


def _when(message: dict) -> datetime.datetime:
    return datetime.datetime.fromisoformat(message["timestamp"].replace("Z", "+00:00"))


def _line(number: str, message: dict) -> str:
    # UNVERIFIED layout: "[local time] sender: text".
    sender = "Me" if message.get("from_me") else number
    stamp = _when(message).strftime("%Y-%m-%d %H:%M:%S")
    return f"[{stamp}] {sender}: {message.get('text', '')}"


@server.tool()
def read_imessages(
    phone_number: Annotated[str, Field(description="Phone number of the contact to read messages from")],
    limit: Annotated[float, Field(description="Maximum number of messages to retrieve (default: 10)")] = 10,
) -> str:
    """Read iMessages from a specific contact"""
    count = _limit(limit)
    number, messages = next(((key, msgs) for key, msgs in state.data["threads"].items()
                             if _same_number(key, phone_number)), (phone_number, []))
    newest = sorted(messages, key=_when, reverse=True)[:count]
    if newest:
        # UNVERIFIED header wording.
        result = (f"Found {len(newest)} message(s) with {number} (most recent first):\n\n"
                  + "\n".join(_line(number, m) for m in newest))
    else:
        result = f"No messages found with {phone_number}."  # UNVERIFIED wording
    state.log_call("read_imessages", {"phone_number": phone_number, "limit": limit}, result)
    return result


@server.tool()
def get_unread_imessages(limit: float = 10) -> str:
    """Get all unread iMessages"""
    count = _limit(limit)
    unread = [(number, m) for number, msgs in state.data["threads"].items()
              for m in msgs if m.get("unread") and not m.get("from_me")]
    unread = sorted(unread, key=lambda pair: _when(pair[1]), reverse=True)[:count]
    if unread:
        # UNVERIFIED header wording; the stub leaves each message unread.
        result = (f"Found {len(unread)} unread message(s):\n\n"
                  + "\n".join(_line(number, m) for number, m in unread))
    else:
        result = "No unread messages."  # UNVERIFIED wording
    state.log_call("get_unread_imessages", {"limit": limit}, result)
    return result


def _contact_matches(person: dict, query: str) -> bool:
    wanted = query.lower()
    if any(wanted in value.lower() for value in [person.get("name", "")] + person.get("emails", [])):
        return True
    digits = _digits(query)
    return bool(digits) and any(digits in _digits(p) or _same_number(p, query)
                                for p in person.get("phones", []))


def _contact_details(person: dict) -> str:
    # UNVERIFIED layout: a line per field, phones and emails comma-joined.
    lines = [f"Name: {person.get('name', '')}"]
    if person.get("phones"):
        lines.append("Phone: " + ", ".join(person["phones"]))
    if person.get("emails"):
        lines.append("Email: " + ", ".join(person["emails"]))
    return "\n".join(lines)


@server.tool()
def search_contacts(query: str) -> str:
    """Search contacts by name, phone, or email"""
    hits = [p for p in state.data["contacts"] if query and _contact_matches(p, query)]
    if hits:
        # UNVERIFIED: a blank line between two people.
        result = f"Found {len(hits)} contact(s):\n\n" + "\n\n".join(_contact_details(p) for p in hits)
    else:
        result = f"No contacts found matching {query!r}."  # UNVERIFIED wording
    state.log_call("search_contacts", {"query": query}, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
