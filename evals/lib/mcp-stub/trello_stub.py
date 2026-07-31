#!/usr/bin/env python3
"""Eval-only fake Trello MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the subset of Trello tools `triage` actually calls,
backed by an in-memory state model instead of the real Trello API. See
common.py's module docstring for the general stub-server design.

Tool names and parameter schemas below were confirmed against a live
connected Trello MCP server (not guessed from SKILL.md prose), so a
skill's real tool calls -- including name-based list/board resolution and
update_card's batch form -- match this stub instead of silently no-oping.

Environment:
  MCP_STUB_STATE_FILE  Path to the seed state JSON (see State Model below).
                        If unset or missing, starts from an empty board set.
  MCP_STUB_STATE_OUT    Path to write the current state to after every tool
                         call -- this is what a grader diffs against an
                         expected-state.json fixture.
  MCP_STUB_LOG           Path to append one JSON line per tool call to, for
                          graders that also want to assert on call sequence.

State model (the fake Trello "database"):
  {
    "boards": {"<board_id>": {"id": "...", "name": "..."}},
    "lists":  {"<list_id>": {"id": "...", "name": "...", "board_id": "..."}},
    "cards":  {"<card_id>": {"id": "...", "name": "...", "desc": "...",
                              "list_id": "...", "board_id": "...",
                              "labels": ["<label_id>", ...],
                              "due": null or "<ISO date>",
                              "due_complete": false,
                              "url": "https://trello.com/c/<id>/<slug>"}},
    "labels": {"<label_id>": {"id": "...", "name": "...", "color": "...",
                               "board_id": "..."}}
  }

Tool surface is intentionally a subset scoped to what `triage`'s
Trello-scoped flow actually needs (Steps 0-4, 8): resolve boards/lists,
fetch cards (list-level and single-card detail), search for duplicates,
audit and apply metadata changes, and manage labels. It does not cover
card creation/move-to-archive/checklists/comments (not exercised by the
initial eval batch, and view_card's checklists/comments are always
returned empty here) or Step 4c's capture-to-Trello flow (that's a
secondary path used when the *primary* scope is Jira/email, not Trello,
and is out of scope for this pilot -- see the plan for sequencing).
"""

import sys

from common import StubState

state = StubState(default={"boards": {}, "lists": {}, "cards": {}, "labels": {}})

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer("trello-stub")


def _resolve_board(board_id: str | None, board_name: str | None) -> str:
    if board_id:
        if board_id not in state.data["boards"]:
            raise ValueError(f"trello-stub: no board with id {board_id!r}")
        return board_id
    if board_name:
        matches = [b["id"] for b in state.data["boards"].values() if b["name"] == board_name]
        if not matches:
            raise ValueError(f"trello-stub: no board named {board_name!r}")
        if len(matches) > 1:
            raise ValueError(f"trello-stub: board name {board_name!r} is ambiguous")
        return matches[0]
    raise ValueError("trello-stub: must provide board_id or board_name")


def _resolve_list(
    list_id: str | None,
    list_name: str | None,
    board_id: str | None,
    board_name: str | None,
) -> str:
    if list_id:
        if list_id not in state.data["lists"]:
            raise ValueError(f"trello-stub: no list with id {list_id!r}")
        return list_id
    if list_name:
        resolved_board = _resolve_board(board_id, board_name)
        matches = [
            lst["id"]
            for lst in state.data["lists"].values()
            if lst["name"] == list_name and lst["board_id"] == resolved_board
        ]
        if not matches:
            raise ValueError(f"trello-stub: no list named {list_name!r} on board {resolved_board!r}")
        if len(matches) > 1:
            raise ValueError(f"trello-stub: list name {list_name!r} is ambiguous on board {resolved_board!r}")
        return matches[0]
    raise ValueError("trello-stub: must provide list_id or list_name")


def _resolve_label(label_ref: str, board_id: str) -> str:
    """A label ref may be an ID or an exact name, scoped to one board."""
    if label_ref in state.data["labels"]:
        return label_ref
    matches = [
        lbl["id"]
        for lbl in state.data["labels"].values()
        if lbl["name"] == label_ref and lbl["board_id"] == board_id
    ]
    if not matches:
        raise ValueError(f"trello-stub: no label {label_ref!r} on board {board_id!r}")
    if len(matches) > 1:
        raise ValueError(f"trello-stub: label name {label_ref!r} is ambiguous on board {board_id!r}")
    return matches[0]


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _card_view(card: dict) -> dict:
    return {
        "id": card["id"],
        "name": card["name"],
        "url": card["url"],
        "labels": card["labels"],
        "due": card["due"],
    }


@server.tool()
def get_boards(include_closed: bool = False) -> list[dict]:
    """List all Trello boards with their IDs. The stub does not model
    closed/archived boards, so include_closed has no effect here."""
    result = [{"id": b["id"], "name": b["name"]} for b in state.data["boards"].values()]
    state.log_call("get_boards", {"include_closed": include_closed}, result)
    return result


@server.tool()
def view_board(board_id: str) -> dict:
    """View a Trello board's lists and card counts."""
    resolved = _resolve_board(board_id, None)
    lists = [
        {
            "id": lst["id"],
            "name": lst["name"],
            "card_count": sum(1 for c in state.data["cards"].values() if c["list_id"] == lst["id"]),
        }
        for lst in state.data["lists"].values()
        if lst["board_id"] == resolved
    ]
    result = {"board_id": resolved, "lists": lists}
    state.log_call("view_board", {"board_id": board_id}, result)
    return result


@server.tool()
def view_list(
    list_id: str | None = None,
    list_name: str | None = None,
    board_id: str | None = None,
    board_name: str | None = None,
) -> dict:
    """View all cards in a Trello list. Provide either list_id (takes
    precedence) or a list_name plus board_name/board_id."""
    resolved = _resolve_list(list_id, list_name, board_id, board_name)
    cards = [_card_view(c) for c in state.data["cards"].values() if c["list_id"] == resolved]
    result = {"list_id": resolved, "cards": cards}
    state.log_call(
        "view_list",
        {"list_id": list_id, "list_name": list_name, "board_id": board_id, "board_name": board_name},
        result,
    )
    return result


@server.tool()
def view_card(card_id: str) -> dict:
    """View full details for a Trello card. The stub does not model
    checklists or comments, so those fields are always returned empty."""
    if card_id not in state.data["cards"]:
        raise ValueError(f"trello-stub: no card with id {card_id!r}")
    card = state.data["cards"][card_id]
    result = dict(card, checklists=[], comments=[])
    state.log_call("view_card", {"card_id": card_id}, result)
    return result


@server.tool()
def search_trello(
    query: str,
    board_id: str | None = None,
    exclude_completed: bool = False,
    limit: int = 10,
    model_types: str = "cards",
    partial: bool = False,
) -> list[dict]:
    """Search Trello for cards, boards, or members (comma-separated
    model_types). The stub only implements card and board search --
    member search is out of scope for this pilot and always returns no
    member results."""
    q = query.lower()
    types = {t.strip() for t in model_types.split(",")}
    result: dict[str, list[dict]] = {}

    if "cards" in types:
        matches = []
        for c in state.data["cards"].values():
            if board_id and c["board_id"] != board_id:
                continue
            if exclude_completed and c.get("due_complete"):
                continue
            if q in c["name"].lower() or q in c["desc"].lower():
                matches.append(
                    {
                        "id": c["id"],
                        "name": c["name"],
                        "url": c["url"],
                        "list_id": c["list_id"],
                        "board_id": c["board_id"],
                    }
                )
        result["cards"] = matches[:limit]

    if "boards" in types:
        result["boards"] = [
            {"id": b["id"], "name": b["name"]}
            for b in state.data["boards"].values()
            if q in b["name"].lower()
        ][:limit]

    if "members" in types:
        result["members"] = []

    flat = [item for items in result.values() for item in items]
    state.log_call(
        "search_trello",
        {
            "query": query,
            "board_id": board_id,
            "exclude_completed": exclude_completed,
            "limit": limit,
            "model_types": model_types,
            "partial": partial,
        },
        flat,
    )
    return flat


@server.tool()
def get_board_labels(board_id: str) -> list[dict]:
    """List all labels defined on a Trello board."""
    resolved = _resolve_board(board_id, None)
    result = [
        {"id": lbl["id"], "name": lbl["name"], "color": lbl["color"]}
        for lbl in state.data["labels"].values()
        if lbl["board_id"] == resolved
    ]
    state.log_call("get_board_labels", {"board_id": board_id}, result)
    return result


@server.tool()
def create_label(
    name: str,
    board_id: str | None = None,
    board_name: str | None = None,
    color: str = "",
) -> dict:
    """Create a new label on a Trello board. Returns the new label's id."""
    resolved = _resolve_board(board_id, board_name)
    new_id = f"label-{len(state.data['labels']) + 1}"
    state.data["labels"][new_id] = {"id": new_id, "name": name, "color": color, "board_id": resolved}
    state.flush()
    result = {"id": new_id, "name": name, "color": color}
    state.log_call(
        "create_label", {"board_id": board_id, "board_name": board_name, "name": name, "color": color}, result
    )
    return result


def _update_one_card(
    card_id: str,
    name,
    desc,
    due,
    due_complete,
    pos,
    list_id,
    list_name,
    board_id,
    board_name,
    add_labels,
    remove_labels,
) -> dict:
    if card_id not in state.data["cards"]:
        raise ValueError(f"trello-stub: no card with id {card_id!r}")
    card = state.data["cards"][card_id]
    if name is not None:
        card["name"] = name
    if desc is not None:
        card["desc"] = desc
    if due is not None:
        card["due"] = due if due != "" else None
    if due_complete is not None:
        card["due_complete"] = due_complete
    if pos is not None:
        card["pos"] = pos
    if list_id is not None or list_name is not None:
        card["list_id"] = _resolve_list(list_id, list_name, board_id, board_name)
        card["board_id"] = state.data["lists"][card["list_id"]]["board_id"]
    for lbl in _as_list(add_labels):
        resolved_lbl = _resolve_label(lbl, card["board_id"])
        if resolved_lbl not in card["labels"]:
            card["labels"].append(resolved_lbl)
    for lbl in _as_list(remove_labels):
        resolved_lbl = _resolve_label(lbl, card["board_id"])
        if resolved_lbl in card["labels"]:
            card["labels"].remove(resolved_lbl)
    return dict(card)


@server.tool()
def update_card(
    card_id: str | list[str],
    name: str | None = None,
    desc: str | None = None,
    due: str | None = None,
    due_complete: bool | None = None,
    pos: str | None = None,
    list_id: str | None = None,
    list_name: str | None = None,
    board_id: str | None = None,
    board_name: str | None = None,
    add_labels: str | list[str] | None = None,
    remove_labels: str | list[str] | None = None,
    timezone: str | None = None,
) -> dict:
    """Update one or more Trello cards. Only provided fields are changed.
    Pass a list of card IDs to apply the same field changes to every card;
    each is attempted independently (no abort on first failure). timezone
    is accepted for schema parity but ignored -- the stub stores due dates
    as given, with no timezone conversion."""
    ids = card_id if isinstance(card_id, list) else [card_id]
    results = []
    for cid in ids:
        try:
            updated = _update_one_card(
                cid, name, desc, due, due_complete, pos, list_id, list_name, board_id, board_name,
                add_labels, remove_labels,
            )
            results.append({"card_id": cid, "ok": True, "card": updated})
        except ValueError as e:
            results.append({"card_id": cid, "ok": False, "error": str(e)})
    state.flush()
    result = {"results": results, "succeeded": sum(1 for r in results if r["ok"]), "failed": sum(1 for r in results if not r["ok"])}
    state.log_call(
        "update_card",
        {
            "card_id": card_id,
            "name": name,
            "desc": desc,
            "due": due,
            "due_complete": due_complete,
            "pos": pos,
            "list_id": list_id,
            "list_name": list_name,
            "board_id": board_id,
            "board_name": board_name,
            "add_labels": add_labels,
            "remove_labels": remove_labels,
            "timezone": timezone,
        },
        result,
    )
    return result


if __name__ == "__main__":
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    server.run(transport="stdio")
