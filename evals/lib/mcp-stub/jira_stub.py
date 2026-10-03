#!/usr/bin/env python3
"""Eval-only fake Jira (Atlassian) MCP server.

A real, protocol-compliant stdio MCP server (built on the official `mcp`
SDK) implementing the subset of Atlassian MCP tools `triage`'s Jira flow
actually needs, backed by an in-memory state model instead of a real Jira
site. See common.py's module docstring for the general stub-server design.

Tool names and parameter schemas below were confirmed against the live
connected Atlassian MCP server (connector-verified, not guessed from
prose), including the cloudId-first flow: every Jira tool requires a
cloudId, which real sessions discover via getAccessibleAtlassianResources,
so the stub serves that too and validates the cloudId on every call.

Environment: MCP_STUB_STATE_FILE / MCP_STUB_STATE_OUT / MCP_STUB_LOG, same
contract as trello_stub.py.

State model (the fake Jira "site"):
  {
    "cloud": {"id": "<uuid-ish>", "url": "https://<site>.atlassian.net",
               "name": "<site>"},
    "projects": {"<KEY>": {"key": "...", "id": "...", "name": "...",
                            "issueTypes": ["Task", "Bug", ...]}},
    "issues": {"<KEY-N>": {
        "key": "...", "id": "...", "project": "<KEY>",
        "summary": "...", "description": "...",
        "status": {"name": "...", "statusCategory": "To Do|In Progress|Done"},
        "issuetype": "...", "priority": null or "...",
        "labels": [...], "assignee": null or {"accountId", "displayName"},
        "reporter": {"accountId", "displayName"},
        "created": "<ISO>", "updated": "<ISO>",
        "resolution": null or "...", "duedate": null or "YYYY-MM-DD",
        "rank": "<sortable string, optional>",
        "comments": [{"id": "...", "body": "...", "created": "<ISO>",
                       "author": {"accountId": "...", "displayName": "..."}}]
    }},
    "stub_now": "<ISO, optional: the stub's fixed 'now'>",
    "users": [{"accountId": "...", "displayName": "...",
                "emailAddress": "..."}],
    "me": {"accountId": "...", "displayName": "..."},
    "transitions": [{"id": "...", "name": "...",
                      "to": {"name": "...", "statusCategory": "..."}}]
  }

A comment's optional "author" is passed through to callers verbatim, and the
optional top-level "me" identifies the fixture's own account: comments this
stub creates are stamped with it. Two users with similar display names and
different accountIds is a fixture worth writing, because attributing writing
by display name is exactly the mistake this lets an eval catch.

getConfluencePage serves a "pages" section of the state, keyed by page id:
  "pages": {"<id>": {"id": "...", "title": "...", "spaceId": "...",
                      "tinyId": "<code from /wiki/x/ URLs>",
                      "body": "<text, or empty for a macro-only page>"}}
Unlike the Jira tools, its response layout is NOT connector-verified. The
parameters match the live tool's schema, but the response is modelled on
the published Confluence Cloud REST v2 "Get page by id" shape (id, status,
title, spaceId, version, body.<format>.value, _links), because no live
response was available to copy. The behaviour it exists to reproduce, a
page built from macros returning an empty body, comes from observed use
rather than documentation; a fixture expresses it with "body": "".

JQL support in searchJiraIssuesUsingJql is a small, documented subset:
clauses joined by AND, each one of `project = KEY`, `status != NAME`,
`statusCategory != NAME` (and the `=` forms), `text ~ "words"` or
`summary ~ "words"` (substring match against summary+description), with an
optional trailing `ORDER BY` over `Rank`, `created`, `updated`,
`duedate`, or `key`, each `ASC` (the default) or `DESC`, comma-separated.
Anything else raises a loud error naming the unsupported construct rather
than silently matching nothing or everything -- the same fail-loud property
as the other stubs.

Issue order: a Jira issue's rank is its position in the backlog, which
Atlassian documents as arranging work items by relative importance, and
`ORDER BY Rank ASC` (accepted by the live connector) lists the top of the
backlog first. A fixture issue's optional "rank" is that position as a
string compared lexically, the way Jira's LexoRank values sort. Rank is a
custom field the live search does not return by default, so the stub never
returns it: the order of the results is the only sign of it. An issue with
no "rank" ranks by its "created" time, so a fixture that sets none reads in
creation order, and one that tests ordering sets a rank on every issue.
Empty values sort last in either direction, an assumption the stub has not
checked against Jira. `ORDER BY priority` is refused rather than guessed:
Jira orders priorities by each site's own priority list, which a fixture does
not model. Without an ORDER BY, results keep the fixture's order; the live
default order is unverified.
"""

import re

from common import StubState

state = StubState(default={"cloud": {"id": "cloud-1", "url": "https://example.atlassian.net", "name": "example"},
                           "projects": {}, "issues": {}, "users": [], "transitions": []})

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer("atlassian-stub")

# Fixed "now" for deterministic updated/created stamps in trial state. A
# fixture can name its own as a top-level "stub_now", which fixture-dates.py
# moves with the rest of its dates; without one, the old fixed value stands.
_STUB_NOW = state.data.get("stub_now", "2026-07-31T16:00:00Z")


def _check_cloud(cloud_id: str) -> None:
    cloud = state.data["cloud"]
    if cloud_id not in (cloud["id"], cloud["url"], cloud["name"]):
        raise ValueError(
            f"jira-stub: unknown cloudId {cloud_id!r} -- use getAccessibleAtlassianResources "
            f"to discover the site (id {cloud['id']!r})"
        )


def _get_issue(issue_id_or_key: str) -> dict:
    if issue_id_or_key not in state.data["issues"]:
        raise ValueError(f"jira-stub: no issue with key {issue_id_or_key!r}")
    return state.data["issues"][issue_id_or_key]


def _issue_view(issue: dict, include_comments: bool = False) -> dict:
    view = {k: v for k, v in issue.items() if k not in ("comments", "rank")}
    if include_comments:
        view["comment"] = {"comments": issue.get("comments", [])}
    return view


def _clause_value(clause: str, field: str, operator: str) -> str | None:
    """The clause's comparison value when it uses `operator`, else None."""
    rest = clause[len(field):].strip()
    if rest.startswith(operator):
        return rest[len(operator):].strip().strip('"\'')
    return None


def _match_project(issue: dict, clause: str) -> bool:
    value = _clause_value(clause, "project", "=")
    if value is None:
        raise ValueError(f"jira-stub: unsupported JQL clause {clause!r} (project supports '=' only)")
    return issue["project"].lower() == value.lower()


def _match_status_field(issue: dict, clause: str, field: str) -> bool:
    actual = issue["status"]["statusCategory"] if field == "statuscategory" else issue["status"]["name"]
    value = _clause_value(clause, field, "!=")
    if value is not None:
        return actual.lower() != value.lower()
    value = _clause_value(clause, field, "=")
    if value is not None:
        return actual.lower() == value.lower()
    raise ValueError(f"jira-stub: unsupported JQL clause {clause!r} ({field} supports '=' and '!=')")


def _match_text_field(issue: dict, clause: str, field: str) -> bool:
    value = _clause_value(clause, field, "~")
    if value is None:
        raise ValueError(f"jira-stub: unsupported JQL clause {clause!r} ({field} supports '~' only)")
    haystack = issue["summary"].lower()
    if field == "text":
        haystack += " " + (issue.get("description") or "").lower()
    return value.lower() in haystack


def _clause_matches(issue: dict, clause: str) -> bool:
    c = clause.strip()
    lower = c.lower()
    if lower.startswith("project"):
        return _match_project(issue, c)
    for field in ("statuscategory", "status"):
        if lower.startswith(field):
            return _match_status_field(issue, c, field)
    for field in ("text", "summary"):
        if lower.startswith(field):
            return _match_text_field(issue, c, field)
    raise ValueError(
        f"jira-stub: unsupported JQL clause {clause!r} -- supported: project =, status =/!=, "
        "statusCategory =/!=, text ~, summary ~, joined by AND, optional trailing ORDER BY"
    )


_ORDER_FIELDS = {
    "rank": lambda i: i.get("rank") or i.get("created") or "",
    "created": lambda i: i.get("created") or "",
    "updated": lambda i: i.get("updated") or "",
    "duedate": lambda i: i.get("duedate") or "",
    "key": lambda i: (i["project"], int(i["key"].rsplit("-", 1)[1])),
}


def _split_order_by(jql: str) -> tuple[str, str]:
    """The JQL's filter part and its ORDER BY terms, either possibly empty."""
    padded = f" {jql}"
    lower = padded.lower()
    if " order by " not in lower:
        return jql, ""
    at = lower.index(" order by ")
    return padded[:at].strip(), padded[at + len(" order by "):].strip()


def _order_issues(issues: list[dict], jql: str) -> list[dict]:
    """Apply the JQL's ORDER BY, last key first so the first key wins.

    Issues with no value for a field sort last whichever the direction
    (see the module docstring)."""
    clause = _split_order_by(jql)[1]
    if not clause:
        return issues
    ordered = list(issues)
    for part in reversed([p.strip() for p in clause.split(",") if p.strip()]):
        words = part.split()
        field = words[0].lower()
        direction = words[1].lower() if len(words) > 1 else "asc"
        if field not in _ORDER_FIELDS or direction not in ("asc", "desc") or len(words) > 2:
            raise ValueError(
                f"jira-stub: unsupported ORDER BY term {part!r} -- supported: "
                "Rank, created, updated, duedate, key, each ASC or DESC"
            )
        key = _ORDER_FIELDS[field]
        present = [i for i in ordered if key(i) != ""]
        empty = [i for i in ordered if key(i) == ""]
        ordered = sorted(present, key=key, reverse=direction == "desc") + empty
    return ordered


def _jql_matches(issue: dict, jql: str) -> bool:
    query = _split_order_by(jql)[0]
    # JQL's AND keyword is case-insensitive, so split accordingly. The
    # whitespace is normalized first so the split can use a literal
    # single-space pattern (no quantifiers, no backtracking). A quoted value
    # containing the word "and" would be split too, but that then hits the
    # unsupported-clause error loudly rather than silently mismatching.
    query = " ".join(query.split())
    clauses = re.split(r" and ", query, flags=re.IGNORECASE)
    return all(_clause_matches(issue, part) for part in clauses if part.strip())


@server.tool()
def getAccessibleAtlassianResources() -> list[dict]:  # NOSONAR(S1542) camelCase = real MCP tool name
    """Get the Atlassian sites (cloud resources) this account can access,
    including each site's cloudId. Call this first: every Jira tool below
    requires the cloudId."""
    cloud = state.data["cloud"]
    result = [{"id": cloud["id"], "url": cloud["url"], "name": cloud["name"]}]
    state.log_call("getAccessibleAtlassianResources", {}, result)
    return result


@server.tool()
def getVisibleJiraProjects(  # NOSONAR(S1542) camelCase = real MCP tool name
    cloudId: str,
    action: str = "create",
    expandIssueTypes: bool = True,
    maxResults: int = 50,
    searchString: str = "",
    startAt: int = 0,
) -> dict:
    """Get projects visible to the user, optionally filtered by
    searchString against the project key or name."""
    _check_cloud(cloudId)
    projects = []
    for p in state.data["projects"].values():
        if searchString and searchString.lower() not in (p["key"] + " " + p["name"]).lower():
            continue
        view = dict(p)
        if not expandIssueTypes:
            view.pop("issueTypes", None)
        projects.append(view)
    result = {"values": projects[startAt:startAt + maxResults], "total": len(projects)}
    state.log_call("getVisibleJiraProjects",
                   {"cloudId": cloudId, "action": action, "searchString": searchString}, result)
    return result


@server.tool()
def searchJiraIssuesUsingJql(  # NOSONAR(S1542) camelCase = real MCP tool name
    cloudId: str,
    jql: str,
    fields: list[str] | None = None,
    maxResults: int = 50,
    nextPageToken: str = "",
    responseContentFormat: str = "markdown",
    searchResultMode: str = "issues",
) -> dict:
    """Search issues with JQL. The stub supports a documented subset:
    project =, status =/!=, statusCategory =/!=, text ~, summary ~, joined
    by AND, with an optional trailing ORDER BY over Rank, created,
    updated, duedate, or key. Unsupported constructs raise an error naming
    the clause."""
    _check_cloud(cloudId)
    include_comments = bool(fields) and ("comment" in fields or "*all" in fields)
    matches = [
        _issue_view(i, include_comments)
        for i in _order_issues([i for i in state.data["issues"].values() if _jql_matches(i, jql)], jql)
    ]
    result: dict = {}
    if searchResultMode in ("issues", "all"):
        result["issues"] = matches[:maxResults]
    if searchResultMode in ("count", "all"):
        result["total"] = len(matches)
    state.log_call("searchJiraIssuesUsingJql",
                   {"cloudId": cloudId, "jql": jql, "fields": fields,
                    "searchResultMode": searchResultMode}, result)
    return result


@server.tool()
def getJiraIssue(  # NOSONAR(S1542) camelCase = real MCP tool name
    cloudId: str,
    issueIdOrKey: str,
    fields: list[str] | None = None,
    expand: str = "",
    responseContentFormat: str = "markdown",
) -> dict:
    """Get issue details. Include "comment" (or "*all") in fields to get
    the issue's comments in comment.comments."""
    _check_cloud(cloudId)
    include_comments = bool(fields) and ("comment" in fields or "*all" in fields)
    result = _issue_view(_get_issue(issueIdOrKey), include_comments)
    state.log_call("getJiraIssue", {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey, "fields": fields}, result)
    return result


@server.tool()
def editJiraIssue(  # NOSONAR(S1542) camelCase = real MCP tool name
    cloudId: str,
    issueIdOrKey: str,
    fields: dict,
    contentFormat: str = "markdown",
    responseContentFormat: str = "markdown",
) -> dict:
    """Update issue fields (summary, description, labels, priority,
    assignee, duedate), keyed by field name. Pass an explicit null to
    clear a field. Returns the updated issue."""
    _check_cloud(cloudId)
    issue = _get_issue(issueIdOrKey)
    editable = {"summary", "description", "labels", "priority", "assignee", "duedate", "resolution"}
    for name, value in fields.items():
        if name not in editable:
            raise ValueError(f"jira-stub: field {name!r} is not editable here -- editable: {sorted(editable)}")
        issue[name] = value
    issue["updated"] = _STUB_NOW
    state.flush()
    result = _issue_view(issue)
    state.log_call("editJiraIssue", {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey, "fields": fields}, result)
    return result


@server.tool()
def addCommentToJiraIssue(  # NOSONAR(S1542) camelCase = real MCP tool name
    cloudId: str,
    issueIdOrKey: str,
    commentBody: str,
    commentId: str = "",
    contentFormat: str = "markdown",
    responseContentFormat: str = "markdown",
) -> dict:
    """Add a comment to an issue, or update an existing one when commentId
    is given."""
    _check_cloud(cloudId)
    issue = _get_issue(issueIdOrKey)
    comments = issue.setdefault("comments", [])
    if commentId:
        for c in comments:
            if c["id"] == commentId:
                c["body"] = commentBody
                result = dict(c)
                break
        else:
            raise ValueError(f"jira-stub: no comment with id {commentId!r} on {issueIdOrKey}")
    else:
        result = {"id": f"comment-{len(comments) + 1}", "body": commentBody,
                  "created": _STUB_NOW}
        # Real comments name their author, and a skill that attributes
        # writing has to read that field rather than infer from the issue.
        if state.data.get("me"):
            result["author"] = dict(state.data["me"])
        comments.append(dict(result))
    issue["updated"] = _STUB_NOW
    state.flush()
    state.log_call("addCommentToJiraIssue",
                   {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey,
                    "commentBody": commentBody, "commentId": commentId}, result)
    return result


@server.tool()
def getTransitionsForJiraIssue(cloudId: str, issueIdOrKey: str) -> dict:  # NOSONAR(S1542) camelCase = real MCP tool name
    """Get the status transitions currently available for an issue."""
    _check_cloud(cloudId)
    _get_issue(issueIdOrKey)
    result = {"transitions": state.data["transitions"]}
    state.log_call("getTransitionsForJiraIssue", {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey}, result)
    return result


@server.tool()
def transitionJiraIssue(cloudId: str, issueIdOrKey: str, transition: dict) -> dict:  # NOSONAR(S1542) camelCase = real MCP tool name
    """Transition an issue's status. transition is {"id": "<transition id>"}
    from getTransitionsForJiraIssue."""
    _check_cloud(cloudId)
    issue = _get_issue(issueIdOrKey)
    tid = transition.get("id")
    for t in state.data["transitions"]:
        if t["id"] == tid:
            issue["status"] = dict(t["to"])
            issue["updated"] = _STUB_NOW
            state.flush()
            result = _issue_view(issue)
            state.log_call("transitionJiraIssue",
                           {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey, "transition": transition}, result)
            return result
    raise ValueError(f"jira-stub: no transition with id {tid!r} -- see getTransitionsForJiraIssue")


@server.tool()
def getConfluencePage(  # NOSONAR(S1542) camelCase = real MCP tool name
    cloudId: str,
    pageId: str,
    contentFormat: str = "markdown",
    contentType: str = "page",
) -> dict:
    """Get a Confluence page or blog post by ID, including body content.
    pageId also accepts a tiny link ID (the encoded part of /wiki/x/ URLs)."""
    _check_cloud(cloudId)
    pages = state.data.get("pages", {})
    page = pages.get(pageId) or next((p for p in pages.values() if p.get("tinyId") == pageId), None)
    if page is None:
        raise ValueError(f"jira-stub: no Confluence page with id or tiny link {pageId!r}")
    base = state.data["cloud"]["url"]
    result = {
        "id": page["id"],
        "status": "current",
        "title": page["title"],
        "spaceId": page.get("spaceId", ""),
        "version": {"number": 1, "createdAt": _STUB_NOW},
        "body": {contentFormat: {"representation": contentFormat, "value": page.get("body", "")}},
        "_links": {"webui": f"{base}/wiki/pages/{page['id']}", "tinyui": f"{base}/wiki/x/{page.get('tinyId', '')}"},
    }
    state.log_call("getConfluencePage",
                   {"cloudId": cloudId, "pageId": pageId, "contentFormat": contentFormat,
                    "contentType": contentType}, result)
    return result


@server.tool()
def lookupJiraAccountId(cloudId: str, searchString: str) -> list[dict]:  # NOSONAR(S1542) camelCase = real MCP tool name
    """Look up user account IDs by display name or email substring."""
    _check_cloud(cloudId)
    needle = searchString.lower()
    result = [
        u for u in state.data["users"]
        if needle in u["displayName"].lower() or needle in u.get("emailAddress", "").lower()
    ]
    state.log_call("lookupJiraAccountId", {"cloudId": cloudId, "searchString": searchString}, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
