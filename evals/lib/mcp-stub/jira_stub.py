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
        "comments": [{"id": "...", "body": "...", "created": "<ISO>"}]
    }},
    "users": [{"accountId": "...", "displayName": "...",
                "emailAddress": "..."}],
    "transitions": [{"id": "...", "name": "...",
                      "to": {"name": "...", "statusCategory": "..."}}]
  }

JQL support in searchJiraIssuesUsingJql is a small, documented subset:
clauses joined by AND, each one of `project = KEY`, `status != NAME`,
`statusCategory != NAME` (and the `=` forms), `text ~ "words"` or
`summary ~ "words"` (substring match against summary+description), with an
optional trailing `ORDER BY ...` (accepted, ignored). Anything else raises
a loud error naming the unsupported construct rather than silently
matching nothing or everything -- the same fail-loud property as the other
stubs.
"""

from common import StubState

state = StubState(default={"cloud": {"id": "cloud-1", "url": "https://example.atlassian.net", "name": "example"},
                           "projects": {}, "issues": {}, "users": [], "transitions": []})

from mcp.server.mcpserver import MCPServer  # noqa: E402

server = MCPServer("atlassian-stub")


def _check_cloud(cloud_id: str) -> None:
    cloud = state.data["cloud"]
    if cloud_id not in (cloud["id"], cloud["url"], cloud["name"]):
        raise ValueError(
            f"jira-stub: unknown cloudId {cloud_id!r} -- use getAccessibleAtlassianResources "
            f"to discover the site (id {cloud['id']!r})"
        )


def _issue_view(issue: dict, include_comments: bool = False) -> dict:
    view = {k: v for k, v in issue.items() if k != "comments"}
    if include_comments:
        view["comment"] = {"comments": issue.get("comments", [])}
    return view


def _clause_matches(issue: dict, clause: str) -> bool:
    c = clause.strip()
    lower = c.lower()
    if lower.startswith("project"):
        rest = c[len("project"):].strip()
        if rest.startswith("="):
            return issue["project"].lower() == rest[1:].strip().strip('"\'').lower()
        raise ValueError(f"jira-stub: unsupported JQL clause {clause!r} (project supports '=' only)")
    for field, getter in (
        ("statuscategory", lambda i: i["status"]["statusCategory"]),
        ("status", lambda i: i["status"]["name"]),
    ):
        if lower.startswith(field):
            rest = c[len(field):].strip()
            if rest.startswith("!="):
                return getter(issue).lower() != rest[2:].strip().strip('"\'').lower()
            if rest.startswith("="):
                return getter(issue).lower() == rest[1:].strip().strip('"\'').lower()
            raise ValueError(f"jira-stub: unsupported JQL clause {clause!r} ({field} supports '=' and '!=')")
    for field in ("text", "summary"):
        if lower.startswith(field):
            rest = c[len(field):].strip()
            if rest.startswith("~"):
                needle = rest[1:].strip().strip('"\'').lower()
                haystack = issue["summary"].lower()
                if field == "text":
                    haystack += " " + (issue.get("description") or "").lower()
                return needle in haystack
            raise ValueError(f"jira-stub: unsupported JQL clause {clause!r} ({field} supports '~' only)")
    raise ValueError(
        f"jira-stub: unsupported JQL clause {clause!r} -- supported: project =, status =/!=, "
        "statusCategory =/!=, text ~, summary ~, joined by AND, optional trailing ORDER BY"
    )


def _jql_matches(issue: dict, jql: str) -> bool:
    query = jql
    lower = query.lower()
    if " order by " in lower:
        query = query[: lower.index(" order by ")]
    return all(_clause_matches(issue, part) for part in query.split(" AND ") if part.strip())


@server.tool()
def getAccessibleAtlassianResources() -> list[dict]:
    """Get the Atlassian sites (cloud resources) this account can access,
    including each site's cloudId. Call this first: every Jira tool below
    requires the cloudId."""
    cloud = state.data["cloud"]
    result = [{"id": cloud["id"], "url": cloud["url"], "name": cloud["name"]}]
    state.log_call("getAccessibleAtlassianResources", {}, result)
    return result


@server.tool()
def getVisibleJiraProjects(
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
def searchJiraIssuesUsingJql(
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
    by AND, with an optional trailing ORDER BY (ignored). Unsupported
    constructs raise an error naming the clause."""
    _check_cloud(cloudId)
    include_comments = bool(fields) and ("comment" in fields or "*all" in fields)
    matches = [
        _issue_view(i, include_comments)
        for i in state.data["issues"].values()
        if _jql_matches(i, jql)
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
def getJiraIssue(
    cloudId: str,
    issueIdOrKey: str,
    fields: list[str] | None = None,
    expand: str = "",
    responseContentFormat: str = "markdown",
) -> dict:
    """Get issue details. Include "comment" (or "*all") in fields to get
    the issue's comments in comment.comments."""
    _check_cloud(cloudId)
    if issueIdOrKey not in state.data["issues"]:
        raise ValueError(f"jira-stub: no issue with key {issueIdOrKey!r}")
    include_comments = bool(fields) and ("comment" in fields or "*all" in fields)
    result = _issue_view(state.data["issues"][issueIdOrKey], include_comments)
    state.log_call("getJiraIssue", {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey, "fields": fields}, result)
    return result


@server.tool()
def editJiraIssue(
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
    if issueIdOrKey not in state.data["issues"]:
        raise ValueError(f"jira-stub: no issue with key {issueIdOrKey!r}")
    issue = state.data["issues"][issueIdOrKey]
    editable = {"summary", "description", "labels", "priority", "assignee", "duedate", "resolution"}
    for name, value in fields.items():
        if name not in editable:
            raise ValueError(f"jira-stub: field {name!r} is not editable here -- editable: {sorted(editable)}")
        issue[name] = value
    issue["updated"] = "2026-07-31T16:00:00Z"
    state.flush()
    result = _issue_view(issue)
    state.log_call("editJiraIssue", {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey, "fields": fields}, result)
    return result


@server.tool()
def addCommentToJiraIssue(
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
    if issueIdOrKey not in state.data["issues"]:
        raise ValueError(f"jira-stub: no issue with key {issueIdOrKey!r}")
    issue = state.data["issues"][issueIdOrKey]
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
                  "created": "2026-07-31T16:00:00Z"}
        comments.append(dict(result))
    issue["updated"] = "2026-07-31T16:00:00Z"
    state.flush()
    state.log_call("addCommentToJiraIssue",
                   {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey,
                    "commentBody": commentBody, "commentId": commentId}, result)
    return result


@server.tool()
def getTransitionsForJiraIssue(cloudId: str, issueIdOrKey: str) -> dict:
    """Get the status transitions currently available for an issue."""
    _check_cloud(cloudId)
    if issueIdOrKey not in state.data["issues"]:
        raise ValueError(f"jira-stub: no issue with key {issueIdOrKey!r}")
    result = {"transitions": state.data["transitions"]}
    state.log_call("getTransitionsForJiraIssue", {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey}, result)
    return result


@server.tool()
def transitionJiraIssue(cloudId: str, issueIdOrKey: str, transition: dict) -> dict:
    """Transition an issue's status. transition is {"id": "<transition id>"}
    from getTransitionsForJiraIssue."""
    _check_cloud(cloudId)
    if issueIdOrKey not in state.data["issues"]:
        raise ValueError(f"jira-stub: no issue with key {issueIdOrKey!r}")
    tid = transition.get("id")
    for t in state.data["transitions"]:
        if t["id"] == tid:
            issue = state.data["issues"][issueIdOrKey]
            issue["status"] = dict(t["to"])
            issue["updated"] = "2026-07-31T16:00:00Z"
            state.flush()
            result = _issue_view(issue)
            state.log_call("transitionJiraIssue",
                           {"cloudId": cloudId, "issueIdOrKey": issueIdOrKey, "transition": transition}, result)
            return result
    raise ValueError(f"jira-stub: no transition with id {tid!r} -- see getTransitionsForJiraIssue")


@server.tool()
def lookupJiraAccountId(cloudId: str, searchString: str) -> list[dict]:
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
