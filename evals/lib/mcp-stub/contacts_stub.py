#!/usr/bin/env python3
"""Eval-only fake Google Contacts MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the two read tools `sift-email` uses to learn who a sender
is: search_contacts and get_contact. In a real session they come from a
custom "Google gap-fill" connector over the People API, alongside its
contact-writing and Gmail-filter tools, which no skill in this repo uses and
this stub leaves out. See common.py's module docstring for the general
stub-server design.

Schema fidelity: tool names and parameter names (query, page_size,
resource_name) were copied from the live connector's schemas, not guessed.
Its responses are one text value, which the SDK returns as {"result":
"..."} exactly as the live tool did. search_contacts' layout was copied
from a live one-match search on 2026-10-10: a "Found N contact(s):" line,
then each person's full details, not a one-line summary. That search also
returned a free-text "Notes" field, which this stub leaves out. Not seen
live, so flagged UNVERIFIED where built: the separator between two people,
the wording when nothing matches, and get_contact's layout, assumed to be
the same details plus the "Group: <name> (contactGroups/<id>)" line its
description documents.

State model (the fake address book):
  {
    "contacts": {"people/c1001": {
        "names": ["Jordan Lee"],
        "emails": ["jordan@example.com"],
        "phones": ["+1 (206) 555-0100 (mobile)"],
        "organizations": ["Riverside United FC — Coach"],
        "relationships": [{"person": "Sam Lee", "type": "Child"}],
        "groups": [{"id": "contactGroups/abc123", "name": "Soccer"}]
    }}
  }

Every field but "names" is optional. search_contacts matches the query, in
any letter case, as a substring of a contact's names, emails, or
organizations, which are the three things the live description says it
searches by ("name, email, or company").

Environment: MCP_STUB_STATE_FILE / MCP_STUB_STATE_OUT / MCP_STUB_LOG, same
contract as trello_stub.py.
"""

from common import StubState

state = StubState(default={"contacts": {}})

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer("contacts-stub")


def _matches(person: dict, query: str) -> bool:
    wanted = query.lower()
    fields = person.get("names", []) + person.get("emails", []) + person.get("organizations", [])
    return any(wanted in value.lower() for value in fields)


def _details(resource_name: str, person: dict) -> str:
    """One person as the live search printed one: a line per field, emails
    and phones comma-joined, then a Relationships section."""
    lines = [f"Name: {n}" for n in person.get("names", [])]
    if person.get("emails"):
        lines.append("Email: " + ", ".join(person["emails"]))
    lines.append(f"Resource: {resource_name}")
    if person.get("phones"):
        lines.append("Phone: " + ", ".join(person["phones"]))
    lines += [f"Organization: {o}" for o in person.get("organizations", [])]
    if person.get("relationships"):
        lines += ["", "Relationships"]
        lines += [f"• {r['person']} ← {r['type']}" for r in person["relationships"]]
    return "\n".join(lines)


@server.tool()
def search_contacts(query: str, page_size: int = 10) -> str:
    """Search the user's Google Contacts (address book, People API) by
    name, email, or company. Returns matching people with their resource
    names."""
    if not 1 <= page_size <= 30:
        raise ValueError("contacts-stub: page_size must be between 1 and 30")
    hits = [(rn, p) for rn, p in state.data["contacts"].items() if query and _matches(p, query)]
    hits = hits[:page_size]
    if hits:
        # UNVERIFIED: a blank line between two people.
        result = f"Found {len(hits)} contact(s):\n\n" + "\n\n".join(_details(rn, p) for rn, p in hits)
    else:
        result = f"No contacts found matching {query!r}."  # UNVERIFIED wording
    state.log_call("search_contacts", {"query": query, "page_size": page_size}, result)
    return result


@server.tool()
def get_contact(resource_name: str) -> str:
    """Retrieve full details for a Google Contact by resource name: every
    name, email, phone, birthday, relationship, and group membership the
    contact holds. Group memberships render as
    'Group: <name> (contactGroups/<id>)'."""
    person = state.data["contacts"].get(resource_name)
    if person is None:
        raise ValueError(f"contacts-stub: no contact with resource name {resource_name!r}")
    # UNVERIFIED: the search layout, plus the group lines the live
    # description documents.
    groups = [f"Group: {g['name']} ({g['id']})" for g in person.get("groups", [])]
    result = _details(resource_name, person) + ("\n\n" + "\n".join(groups) if groups else "")
    state.log_call("get_contact", {"resource_name": resource_name}, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
