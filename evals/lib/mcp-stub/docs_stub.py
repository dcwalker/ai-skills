#!/usr/bin/env python3
"""Eval-only fake Claude Docs MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the subset of the Claude Docs connector that `sift-email`
uses to keep its rubric and log: create a doc, add and replace blocks, read
a tab, and comment on words, reply in a thread, resolve, and list comments.
See common.py's module docstring for the general stub-server design.

Schema fidelity: tool names (batch, update, read, create, query, guide) and
their top-level parameters (container, batch, ref, engine, payload, object,
answering, opId, verbose) were copied from the live connector's schemas.
Call shapes and response layouts follow the live connector's guide topics
(topic.index, topic.editing, topic.comments) and a cloud routine's live
calls on 2026-10-10: a doc birth through `batch` with `container.create`,
an `insert` at the root's end, an utterance anchored with a `find`, a tab
read, and a comment query. Those five responses are copied in shape. The
rest (replies, resolves, block replaces and deletes, guards, refusals) is
built from the guide's wording and is UNVERIFIED against a live response.

What this stub leaves out: tabs beyond the first, tables edited by cell,
charts and widgets, uploads, move and restore ops, renames, `atRev` history
reads, and the `delete` tool. A call that needs one is refused with
`unsupported`, naming what the stub does support, so a fixture gap shows in
the log instead of silently succeeding. Markdown is kept as written: each
blank-line-separated chunk is one block, and a list or table is one block
rather than one per item or row.

The real connector teaches its call shapes through its server instructions
and `guide` topics. This stub's instructions and `guide` return a condensed
version covering only what it implements, with the same shapes.

State model (the fake doc store):
  {
    "me": {"principal": "u_me", "name": "Pat Example"},
    "docs": {"<doc id>": {"name": "...", "tabs": [
        {"id": "<tab id>", "name": "...", "node": "<body id>"}]}},
    "nodes": {"<body id>": {"doc": "<doc id>", "rev": 1, "blocks": [
        {"id": "<session>.<n>", "kind": "heading" | "paragraph" | "list"
         | "table" | "code" | "pending", "markdown": "...", "rev": 1,
         "intent": "<pending blocks only>"}]}},
    "comments": [{"seq": 1, "at": "<ISO>", "verb": "create", "id": "...",
                  "node": "<body id>", "actor": {...},
                  "payload": {"value": {"body": "...", "parent": {...}}}}]
  }

Every top-level key is optional. "me" names the person Claude acts for. A
comment this stub creates gets the actor the live query returned for a
comment made through MCP: {"principal", "channel": "external", "via":
"mcp", "self": true, "name"}. So Claude's own comments are attributed to
the user, exactly as live. A fixture's seeded comments carry whatever actor
the fixture gives them; a comment the user typed in the doc's editor has no
documented actor layout, so a fixture should give it a "via" other than
"mcp" (the stub's resolve rule below reads it).

Resolves: the guide says a resolve of a thread "a person wrote in" is
refused. Every actor here is the same person, so the stub reads "a person
wrote in" as "a row in the thread has an actor whose via is not mcp". That
reading is UNVERIFIED.

Environment: MCP_STUB_STATE_FILE / MCP_STUB_STATE_OUT / MCP_STUB_LOG, same
contract as trello_stub.py.
"""

import copy
import datetime
import hashlib
import json
import re
import uuid
from typing import Annotated

from pydantic import Field

from common import StubState

state = StubState(default={})
for _key, _empty in (("docs", {}), ("nodes", {}), ("comments", [])):
    state.data.setdefault(_key, _empty)

from mcp.server.mcpserver import MCPServer  # noqa: E402

_INSTRUCTIONS = """Claude Docs (eval stub): docs you create and edit here.
Make a doc with ONE batch call: batch(container={"kind":"project","create":{"name":"<title>","doc":{"markdown":"# <title>\\n\\n<body>","blocks":{...chips, optional}}}}, batch=[]).
The ack's "lids" gives the tab id (f) and its body id (n); "created.link" is the doc's link.
Read a doc: read(ref={"object":"project","id":"<doc id or link>"}) lists its tabs; read(ref={"object":"node","id":"<body id>"}, container={"kind":"project","id":"<doc id>"}, engine="prose") returns the body as xml with block ids and h hashes.
Edit: update(ref={"object":"node","id":"<body id>"}, container=C, engine="prose", payload={"ops":[...]}). Ops: insert, replace, delete. guide(items=["topic.index"]) has the shapes.
Comments: create(object="utterance", container=C, payload={"value":{"body":"...","parent":{"object":"node","id":"<body id>","anchor":{"kind":"find","text":"<words in the doc>"}}}}); reply with parent {"object":"utterance","id":"<thread id>"}; list with query(object="utterance", container=C, payload={"under":{"object":"node","id":"<body id>"}})."""

server = MCPServer("docs-stub", instructions=_INSTRUCTIONS)

# The live connector names this parameter opId. A validation alias publishes
# that name in each tool's schema and accepts only it, while the Python
# parameter stays snake_case.
OpIdArg = Annotated[str | None, Field(validation_alias="opId")]

_GUIDE = {
    "topic.index": """# topic.index (eval stub, condensed)
C = {"kind":"project","id":"<doc id>"}.
Create: batch(container={"kind":"project","create":{"name":"T","doc":{"markdown":"# T\\n\\n<?claude block s1?>","blocks":{"s1":{"type":"pending","intent":"what comes"}}}}}, batch=[]) -> acks, lids {f: tab id, n: body id}, created {link}.
Read: read(ref={"object":"project","id":"<doc id>"}) -> files [{id, name, content {kind:"node", id, engine:"prose"}}]. read(ref={"object":"node","id":"<body id>"}, container=C, engine="prose", payload?) -> data.xml; payload {"kind":"view","sinceRev":N} returns only blocks changed after rev N.
Edit: update(ref={"object":"node","id":"<body id>"}, container=C, engine="prose", payload={"ops":[op, ...]}):
- insert: {"op":"insert","target":{"kind":"root"},"side":"end"|"start","source":{"from":{"kind":"inline","content":"<markdown>"},"as":"markdown"}}, or target {"kind":"blocks","ids":["<block id>"]} with side "before"|"after".
- replace words: {"op":"replace","target":{"kind":"find","text":"<exact words>"},"with":{"from":{"kind":"inline","content":"<new words>"},"as":"text"}}.
- replace a block: {"op":"replace","target":{"kind":"blocks","ids":["<id>"]},"ifHash":"<h>","ifRev":<rev of the read>,"with":{"from":{"kind":"inline","content":"<markdown>"},"as":"markdown"}}; a pending block needs no guard.
- delete: {"op":"delete","target":{"kind":"find","text":"<exact words>"}} or a block target with ifHash + ifRev.
Chips: "blocks" beside "from" (or in doc) maps keys to {"type":"pending","intent"} | {"type":"date","value":"YYYY-MM-DD"} | {"type":"mention","user":"me"}; the text holds <?claude block key?>.""",
    "topic.editing": """# topic.editing (eval stub, condensed)
Op shapes, inside update(ref={"object":"node","id":"<body id>"}, container=C, engine="prose", payload={"ops":[...]}):
- insert: {"op":"insert","target":{"kind":"root"},"side":"end"|"start","source":{"from":{"kind":"inline","content":"<markdown>"},"as":"markdown"}}, or target {"kind":"blocks","ids":["<block id>"]} with side "before"|"after".
- replace words: {"op":"replace","target":{"kind":"find","text":"<exact words>"},"with":{"from":{"kind":"inline","content":"<new words>"},"as":"text"}}.
- replace a block: {"op":"replace","target":{"kind":"blocks","ids":["<id>"]},"ifHash":"<h>","ifRev":<rev>,"with":{"from":{"kind":"inline","content":"<markdown>"},"as":"markdown"}}.
- delete: {"op":"delete","target":{"kind":"find","text":"<exact words>"}} or a block target with ifHash + ifRev.
In a batch, an op is never a member by itself: wrap it as {"verb":"update","ref":{"object":"node","id":"<body id>"},"engine":"prose","payload":{"ops":[...]}}.
Guards: a whole-block replace or delete carries "ifHash" (the block's h) and "ifRev" (the rev of the read that showed it), or "force":true. Missing -> missing_guard; a changed block -> guard_mismatch. Words not found -> find_none. Re-read the block and retry.
Supported ops: insert, replace, delete. Others are refused as unsupported.""",
    "topic.comments": """# topic.comments (eval stub, condensed)
Comment on words: create(object="utterance", container=C, payload={"value":{"body":"...","parent":{"object":"node","id":"<body id>","anchor":{"kind":"find","text":"<3-6 words exactly as in the doc>"}}}}).
Reply: parent {"object":"utterance","id":"<thread's first comment id>"}, no anchor.
Resolve: value {"kind":"resolve"} with parent the thread; refused when a person wrote in the thread.
List: query(object="utterance", container=C, payload={"under":{"object":"node","id":"<body id>"}, "afterSeq"?: N}) -> rows [{seq, at, verb, id, actor, payload}]; under {"object":"utterance","id":"<thread id>"} lists one thread.""",
}

_SESSION = "stub" + uuid.uuid4().hex[:7]
_counter = [0]
_TOKEN = re.compile(r"<\?claude block ([A-Za-z0-9_-]+)\?>")
_SUPPORTED = "supported: batch create, update ops insert/replace/delete, read of a doc or body, create/query of utterances"


def _new_block_id() -> str:
    _counter[0] += 1
    return f"{_SESSION}.{_counter[0]}"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:8]


def _refuse(reason: str, hint: str, **extra) -> None:
    """Raise a refusal as the live connector reports one: a tool error whose
    text is a JSON object with verdict "deny" and a reason."""
    raise ValueError(json.dumps({"verdict": "deny", "reason": reason, "hint": hint, **extra}))


def _doc_id(value: str) -> str:
    """A doc id, from a bare id or a whole claude.ai artifact link."""
    tail = value.split("?")[0].split("#")[0].rstrip("/").rsplit("/", 1)[-1]
    for doc_id in state.data["docs"]:
        if tail == doc_id or tail.endswith("-" + doc_id):
            return doc_id
    return tail


def _doc(value: str) -> tuple[str, dict]:
    doc_id = _doc_id(value or "")
    if doc_id not in state.data["docs"]:
        _refuse("access", "this doc is not shared with you (or not with the access this action needs), "
                          "or no doc has this id -- the cases answer alike by design.")
    return doc_id, state.data["docs"][doc_id]


def _node(node_id: str) -> dict:
    node = state.data["nodes"].get(node_id)
    if node is None:
        _refuse("access", f"no body with id {node_id!r} that you can see")
    return node


def _kind(markdown: str) -> str:
    first = markdown.lstrip()
    if first.startswith("#"):
        return "heading"
    if first.startswith("```"):
        return "code"
    if first.startswith("|"):
        return "table"
    if re.match(r"([-*+]|\d+\.)\s", first):
        return "list"
    return "paragraph"


def _render_chip(chip: dict) -> str:
    kind = chip.get("type")
    if kind == "mention":
        return "@me" if chip.get("user") == "me" else "@" + str(chip.get("user") or chip.get("ref", ""))
    if kind == "date":
        return str(chip.get("value", ""))
    return f"[{kind}]"


def _blocks_from_markdown(markdown: str, chips: dict | None, rev: int) -> list:
    """Split markdown into blocks, one per blank-line-separated chunk. A
    chunk that is exactly one pending-block token becomes a pending block;
    other chip tokens are rendered as plain text."""
    chips = chips or {}
    blocks = []
    for chunk in re.split(r"\n\s*\n", markdown.strip()):
        if not chunk.strip():
            continue
        token = _TOKEN.fullmatch(chunk.strip())
        if token and chips.get(token.group(1), {}).get("type") == "pending":
            blocks.append({"id": _new_block_id(), "kind": "pending", "markdown": "",
                           "intent": chips[token.group(1)].get("intent", ""), "rev": rev})
            continue
        text = _TOKEN.sub(lambda m: _render_chip(chips.get(m.group(1), {"type": "unknown"})), chunk)
        blocks.append({"id": _new_block_id(), "kind": _kind(text), "markdown": text, "rev": rev})
    return blocks


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;")


def _block_xml(block: dict, node_id: str) -> str:
    h = _hash(block["markdown"] + block.get("intent", ""))
    if block["kind"] == "pending":
        return f"<pending id='{block['id']}' h='{h}' intent='{_escape(block['intent'])}'/>"
    markers = "".join(f"<comment id='{c['id']}'/>" for c in state.data["comments"]
                      if c.get("node") == node_id
                      and c["payload"]["value"].get("parent", {}).get("anchor", {}).get("block") == block["id"])
    tag = "paragraph" if block["kind"] in ("heading", "paragraph") else block["kind"]
    heading, text = "", block["markdown"]
    if block["kind"] == "heading":
        # The live read shows a heading's level as an attribute and its text
        # without the leading #s.
        text = text.lstrip()
        heading = f" heading='{len(text) - len(text.lstrip('#'))}'"
        text = text.lstrip("#").strip()
    return (f"<{tag} id='{block['id']}' rev='{block['rev']}' h='{h}'{heading}>"
            f"{markers}{_escape(text)}</{tag}>")


def _xml(node_id: str, blocks: list, op: int | None = None) -> str:
    opening = "<doc>" if op is None else f"<doc op='{op}'>"
    return opening + "".join(_block_xml(b, node_id) for b in blocks) + "</doc>"


def _index(node: dict, block_id: str) -> int:
    for i, block in enumerate(node["blocks"]):
        if block["id"] == block_id:
            return i
    _refuse("block_gone", f"no block {block_id!r} in this body; read it again")
    return -1


def _check_guard(op: dict, blocks: list) -> None:
    if op.get("force") or all(b["kind"] == "pending" for b in blocks):
        return
    if "ifRev" not in op or (len(blocks) == 1 and "ifHash" not in op):
        _refuse("missing_guard", "a whole-block replace or delete carries ifHash (the block's h) "
                                 "and ifRev (the rev of the read that showed it), or force:true")
    if len(blocks) == 1 and op["ifHash"] != _hash(blocks[0]["markdown"] + blocks[0].get("intent", "")):
        _refuse("guard_mismatch", "that block changed after your read; it is shown as it stands",
                data={"xml": _block_xml(blocks[0], ""), "rev": blocks[0]["rev"]})


def _find(node: dict, text: str, nth: int = 1) -> dict:
    seen = 0
    for block in node["blocks"]:
        count = block["markdown"].count(text) if text else 0
        if seen + count >= nth:
            return block
        seen += count
    _refuse("find_none", f"the words {text!r} are not in this body as quoted; re-read the block and quote it again")
    return {}


def _source(op: dict, key: str) -> tuple[str, str, dict]:
    spec = op.get(key) or {}
    origin = spec.get("from") or {}
    if origin.get("kind") != "inline" or not isinstance(origin.get("content"), str):
        _refuse("bad_source", f"{key}.from must be {{\"kind\":\"inline\",\"content\":\"...\"}}")
    return origin["content"], spec.get("as", "markdown"), spec.get("blocks") or {}


def _insert_index(node: dict, op: dict, target: dict) -> int:
    """Where an insert lands: the root's start or end, or beside a block."""
    side = op.get("side")
    if target.get("kind") == "root":
        if side not in ("end", "start"):
            _refuse("bad_side", "insert at the root takes side \"end\" or \"start\"")
        return 0 if side == "start" else len(node["blocks"])
    if target.get("kind") == "blocks" and target.get("ids"):
        if side not in ("before", "after"):
            _refuse("bad_side", "insert beside a block takes side \"before\" or \"after\"")
        return _index(node, target["ids"][0]) + (0 if side == "before" else 1)
    _refuse("bad_target", "insert takes target {kind:root} or {kind:blocks, ids:[...]}")
    return 0


def _edit_words(node: dict, target: dict, replacement: str, rev: int) -> list:
    """Replace the quoted words (or delete them, with an empty replacement)."""
    block = _find(node, target.get("text", ""), target.get("nth", 1))
    block["markdown"] = block["markdown"].replace(target["text"], replacement, 1)
    block["rev"] = rev
    return [block]


def _target_blocks(node: dict, op: dict, target: dict) -> list:
    """The blocks a whole-block op names, after its guard is checked."""
    olds = [node["blocks"][_index(node, i)] for i in target["ids"]]
    _check_guard(op, olds)
    return olds


def _op_insert(node: dict, op: dict, target: dict, rev: int) -> list:
    content, _, chips = _source(op, "source")
    new = _blocks_from_markdown(content, chips, rev)
    at = _insert_index(node, op, target)
    node["blocks"][at:at] = new
    return new


def _op_replace(node: dict, op: dict, target: dict, rev: int) -> list:
    content, _, chips = _source(op, "with")
    if target.get("kind") == "find":
        return _edit_words(node, target, content, rev)
    if target.get("kind") == "blocks" and target.get("ids"):
        first = _index(node, target["ids"][0])
        olds = _target_blocks(node, op, target)
        new = _blocks_from_markdown(content, chips, rev)
        for old in olds:
            node["blocks"].remove(old)
        node["blocks"][first:first] = new
        return new
    _refuse("bad_target", "replace takes target {kind:find, text} or {kind:blocks, ids:[...]}")
    return []


def _op_delete(node: dict, op: dict, target: dict, rev: int) -> list:
    if target.get("kind") == "find":
        return _edit_words(node, target, "", rev)
    if target.get("kind") == "blocks" and target.get("ids"):
        olds = _target_blocks(node, op, target)
        if len(olds) == len(node["blocks"]):
            _refuse("last_block", "a tab keeps one block; replace it instead")
        for old in olds:
            node["blocks"].remove(old)
        return []
    _refuse("bad_target", "delete takes target {kind:find, text} or {kind:blocks, ids:[...]}")
    return []


_OPS = {"insert": _op_insert, "replace": _op_replace, "delete": _op_delete}


def _apply_op(node: dict, op: dict, rev: int) -> list:
    """Apply one prose op to a body; returns the blocks it wrote."""
    handler = _OPS.get(op.get("op"))
    if handler is None:
        _refuse("unsupported", f"op {op.get('op')!r} is not implemented by this stub ({_SUPPORTED})")
    return handler(node, op, op.get("target") or {}, rev)


def _payload(payload):
    """The live schema types payload as an object or a string, so a JSON
    string is read as the object it spells."""
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except ValueError:
            _refuse("bad_payload", "payload is an object, or a string holding one as JSON")
    return payload


def _update_node(node_id: str, payload, answering: str | None) -> dict:
    node = _node(node_id)
    payload = _payload(payload)
    ops = (payload or {}).get("ops") if isinstance(payload, dict) else None
    if not isinstance(ops, list) or not ops:
        _refuse("bad_payload", "payload must be {\"ops\":[...]}")
    staged = copy.deepcopy(node)
    rev = staged["rev"] + 1
    xml = "".join(_xml(node_id, _apply_op(staged, op, rev), op=i) for i, op in enumerate(ops))
    staged["rev"] = rev
    node.clear()
    node.update(staged)
    result = {"verdict": "allow", "rev": rev, "session": _SESSION, "xml": xml}
    if answering:
        result["answering"] = answering
    return result


def _actor() -> dict:
    me = state.data.get("me") or {}
    return {"principal": me.get("principal", "u_me"), "channel": "external", "via": "mcp",
            "self": True, "name": me.get("name", "Me")}


def _thread_rows(root_id: str) -> list:
    return [c for c in state.data["comments"]
            if c["id"] == root_id or c["payload"]["value"].get("parent", {}).get("id") == root_id]


def _comment_on_body(container: dict | None, parent: dict) -> tuple[str, dict, dict]:
    """A new thread anchored on words in a body: its node, stored parent, and
    the anchor the response reports."""
    node = _node(parent.get("id", ""))
    if container:
        _doc(container.get("id", ""))
    anchor = parent.get("anchor") or {}
    if anchor.get("kind") != "find" or not anchor.get("text"):
        _refuse("bad_anchor", "a comment on a body needs anchor {kind:find, text:<words in the doc>}")
    block = _find(node, anchor["text"], anchor.get("nth", 1))
    stored = {"object": "node", "id": parent["id"],
              "anchor": {"kind": "chars", "block": block["id"], "quote": anchor["text"]}}
    return parent["id"], stored, {"anchor": {"quote": anchor["text"], "block": block["id"]}}


def _reply_in_thread(parent: dict, value: dict) -> tuple[str, dict, dict]:
    """A reply or resolve under an existing thread."""
    roots = [c for c in state.data["comments"] if c["id"] == parent.get("id")]
    if not roots:
        _refuse("access", f"no comment with id {parent.get('id')!r} that you can see")
    if value.get("kind") == "resolve" and any(
            r["actor"].get("via") != "mcp" for r in _thread_rows(parent["id"])):
        _refuse("not_yours", "a person wrote in this thread; it is theirs to resolve")
    return roots[0]["node"], {"object": "utterance", "id": parent["id"]}, {}


def _check_body(value: dict) -> None:
    if value.get("kind") != "resolve" and not str(value.get("body", "")).strip():
        _refuse("bad_payload", "a comment needs a non-empty body")
    if len(str(value.get("body", "")).encode()) > 4096:
        _refuse("row_too_large", "comment bodies are limited to 4096 bytes", dim="body")


def _create_utterance(container: dict | None, payload) -> dict:
    payload = _payload(payload)
    value = (payload or {}).get("value") if isinstance(payload, dict) else None
    if not isinstance(value, dict):
        _refuse("bad_payload", "payload is {\"value\":{\"body\":...,\"parent\":{...}}}")
    parent = value.get("parent") or {}
    if parent.get("object") == "node":
        node_id, stored_parent, response_extra = _comment_on_body(container, parent)
    elif parent.get("object") == "utterance":
        node_id, stored_parent, response_extra = _reply_in_thread(parent, value)
    else:
        _refuse("bad_parent", "parent is {object:node, id, anchor} or {object:utterance, id}")
    _check_body(value)
    seq = max((c["seq"] for c in state.data["comments"]), default=0) + 1
    row_id = str(uuid.uuid4())
    stored_value = {k: v for k, v in value.items() if k != "parent"}
    stored_value["parent"] = stored_parent
    state.data["comments"].append({"seq": seq, "at": _now(), "verb": "create", "id": row_id,
                                   "node": node_id, "actor": _actor(),
                                   "payload": {"value": stored_value}})
    return {"verdict": "allow", **response_extra, "minted": row_id}


def _create_doc(spec: dict) -> dict:
    """A doc birth: one tab whose body holds the given markdown."""
    doc_spec = spec.get("doc") or {}
    doc_id, tab_id, node_id = str(uuid.uuid4()), uuid.uuid4().hex[:12], uuid.uuid4().hex[:12]
    blocks = _blocks_from_markdown(doc_spec.get("markdown", ""), doc_spec.get("blocks"), 1)
    if not blocks:
        blocks = [{"id": _new_block_id(), "kind": "paragraph", "markdown": "", "rev": 1}]
    name = spec.get("name") or "Untitled"
    state.data["docs"][doc_id] = {"name": name, "tabs": [{"id": tab_id, "name": name, "node": node_id}]}
    state.data["nodes"][node_id] = {"doc": doc_id, "rev": 1, "blocks": blocks}
    return {"verdict": "allow",
            "acks": [{"verdict": "allow", "minted": tab_id},
                     {"verdict": "allow", "id": node_id, "rev": 1, "session": _SESSION,
                      "xml": _xml(node_id, blocks)}],
            "lids": {"f": tab_id, "n": node_id},
            "created": {"bound": True, "id": doc_id, "link": f"https://claude.ai/code/artifact/{doc_id}"}}


def _apply_member(container: dict, member: dict) -> dict:
    if member.get("verb") == "create" and member.get("object") == "utterance":
        return _create_utterance(container, member.get("payload"))
    if member.get("verb") == "update" and (member.get("ref") or {}).get("object") == "node":
        return _update_node(member["ref"]["id"], member.get("payload"), None)
    _refuse("unsupported", f"batch member {member!r} is not implemented ({_SUPPORTED})")
    return {}


def _apply_members(container: dict, members: list) -> list:
    """Apply a batch's members atomically: a refused member leaves the doc as
    it was before the batch, not with the earlier members in."""
    saved = copy.deepcopy({key: state.data[key] for key in ("nodes", "comments")})
    try:
        return [_apply_member(container, member) for member in members]
    except ValueError:
        state.data.update(saved)
        raise


@server.tool()
def guide(items: list[str] | None = None) -> str:
    """Docs guides: topic.index, topic.editing, topic.comments (condensed
    to what this eval stub implements)."""
    wanted = items or ["topic.index"]
    # A bare topic name ("editing") finds its topic too, rather than leaving a
    # trial to guess call shapes after a refusal.
    result = "\n\n".join(_GUIDE.get(i) or _GUIDE.get(f"topic.{i}")
                           or f"# {i}\n(not available in this eval stub; {_SUPPORTED})" for i in wanted)
    state.log_call("guide", {"items": wanted}, "<guide text>")
    return result


@server.tool()
def batch(container: dict | None = None, batch: list | None = None, op_id: OpIdArg = None,
          verbose: bool | None = None) -> dict:
    """Create a doc, or apply several operations to one doc atomically."""
    args = {"container": container, "batch": batch, "opId": op_id}
    container = container or {}
    try:
        if "create" in container:
            result = _create_doc(container["create"] or {})
        else:
            _doc(container.get("id", ""))
            result = {"verdict": "allow", "acks": _apply_members(container, batch or [])}
    except ValueError as refusal:
        state.log_call("batch", args, {"error": str(refusal)})
        raise
    state.flush()
    state.log_call("batch", args, result)
    return result


@server.tool()
def update(ref: dict, payload: dict | str, container: dict | None = None, engine: str | None = None,
           op_id: OpIdArg = None, answering: str | None = None, verbose: bool | None = None) -> dict:
    """Edit a tab's contents."""
    args = {"ref": ref, "payload": payload, "container": container, "engine": engine, "answering": answering}
    try:
        if (ref or {}).get("object") != "node":
            _refuse("unsupported", f"update of {ref!r} is not implemented ({_SUPPORTED})")
        if container:
            _doc(container.get("id", ""))
        result = _update_node(ref["id"], payload, answering)
    except ValueError as refusal:
        state.log_call("update", args, {"error": str(refusal)})
        raise
    state.flush()
    state.log_call("update", args, result)
    return result


@server.tool()
def read(ref: dict, container: dict | None = None, engine: str | None = None,
         payload: dict | str | None = None) -> dict:
    """Read a doc (lists its tabs), a tab's contents, or a comment."""
    args = {"ref": ref, "container": container, "engine": engine, "payload": payload}
    try:
        kind = (ref or {}).get("object")
        if kind == "project":
            doc_id, doc = _doc(ref.get("id", ""))
            result = {"verdict": "allow", "id": doc_id, "name": doc["name"],
                      "files": [{"id": t["id"], "name": t["name"],
                                 "content": {"kind": "node", "id": t["node"], "engine": "prose"}}
                                for t in doc["tabs"]]}
        elif kind == "node":
            node = _node(ref.get("id", ""))
            blocks = node["blocks"]
            options = _payload(payload) or {}
            if options.get("kind") == "view" and "sinceRev" in options:
                blocks = [b for b in blocks if b["rev"] > options["sinceRev"]]
            elif options.get("kind") == "search":
                blocks = [b for b in blocks if options.get("text", "") in b["markdown"]]
            xml = _xml(ref["id"], blocks).replace("<doc>", f"<doc node='{ref['id']}' rev='{node['rev']}'>", 1)
            result = {"verdict": "allow", "rev": node["rev"], "data": {"rev": node["rev"], "xml": xml}}
        elif kind == "utterance":
            rows = [c for c in state.data["comments"] if c["id"] == ref.get("id")]
            if not rows:
                _refuse("access", f"no comment with id {ref.get('id')!r} that you can see")
            result = {"verdict": "allow", "row": rows[0]}
        else:
            _refuse("unsupported", f"read of {ref!r} is not implemented ({_SUPPORTED})")
    except ValueError as refusal:
        state.log_call("read", args, {"error": str(refusal)})
        raise
    state.log_call("read", args, result)
    return result


@server.tool()
def create(object: str, payload: dict | str, container: dict | None = None, artifact: str | None = None,
           engine: str | None = None, op_id: OpIdArg = None, verbose: bool | None = None) -> dict:
    """Create one object in a doc: a comment (utterance)."""
    args = {"object": object, "payload": payload, "container": container}
    try:
        if object != "utterance":
            _refuse("unsupported", f"create of {object!r} is not implemented ({_SUPPORTED})")
        result = _create_utterance(container, payload)
    except ValueError as refusal:
        state.log_call("create", args, {"error": str(refusal)})
        raise
    state.flush()
    state.log_call("create", args, result)
    return result


@server.tool()
def query(object: str = "utterance", container: dict | None = None, payload: dict | str | None = None) -> dict:
    """List a tab's or a doc's comment history (threads, replies, resolves)."""
    args = {"object": object, "container": container, "payload": payload}
    try:
        if container:
            _doc(container.get("id", ""))
        options = _payload(payload) or {}
        under = options.get("under") or {}
        rows = state.data["comments"]
        if under.get("object") == "node":
            rows = [c for c in rows if c["node"] == under.get("id")]
        elif under.get("object") == "utterance":
            rows = _thread_rows(under.get("id", ""))
        elif under.get("object") == "file":
            nodes = {t["node"] for d in state.data["docs"].values() for t in d["tabs"] if t["id"] == under.get("id")}
            rows = [c for c in rows if c["node"] in nodes]
        if "afterSeq" in options:
            rows = [c for c in rows if c["seq"] > options["afterSeq"]]
        if options.get("limit"):
            rows = rows[:options["limit"]]
        result = {"verdict": "allow",
                  "rows": [{k: v for k, v in c.items() if k != "node"} for c in rows]}
    except ValueError as refusal:
        state.log_call("query", args, {"error": str(refusal)})
        raise
    state.log_call("query", args, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
