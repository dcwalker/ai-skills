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
        "creator": null or {"accountId", "displayName"} (optional),
        "created": "<ISO>", "updated": "<ISO>",
        "resolution": null or "...", "duedate": null or "YYYY-MM-DD",
        "rank": "<sortable string, optional>",
        "comments": [{"id": "...", "body": "...", "created": "<ISO>",
                       "author": {"accountId": "...", "displayName": "..."}}]
    }},
    "stub_now": "<ISO, optional: the stub's fixed 'now'>",
    "timeZone": "<IANA zone, optional: the account's Jira profile time zone>",
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

The Confluence search and version tools serve the same "pages" section.
A page that a meeting-window search should find adds these optional fields:
  "subType": "live" (a live doc; omit for a regular page),
  "space": "<space title>", "spaceKey": "<KEY>", "excerpt": "...",
  "versions": [{"number": 1, "authorId": "<account ID>",
                "createdAt": "<ISO>", "collaborators": ["<account ID>", ...],
                "message": "", "body": "<markdown at that version>"}]
A page without "versions" has one, by "me", at the stub's fixed now.
Their layouts come from live responses recorded on Nov 3, 2026 (Trello
card 82246), with unused fields left out:
  searchConfluence(cql)            {"data": {"results": [...], "totalSize", "_links"}}
  listConfluenceContentVersions    {"data": {"results": [version, ...]}}, newest first
  executeRead(name, arguments) runs getConfluenceContentVersion,
  diffConfluenceContentVersions, and getPeopleInfo.
A search result's "lastModified" is the latest version's "createdAt"
truncated to whole seconds: when that editing session started. A version's
"collaborators" lists every account that edited in its session, the author
included. getPeopleInfo resolves account IDs from "users".

CQL support in searchConfluence is a small, documented subset: clauses
joined by AND, each one of `contributor = "<id>"` (any version's author or
collaborator), `creator = "<id>"` (version 1's author), `type = page` or
`type in (page, live)`, `space = KEY`, `title ~ "<words>"` (the title),
`text ~` or `siteSearch ~ "<words>"` (title, excerpt, and current body,
both a case-insensitive substring match), and `created` or `lastmodified`
compared with `>=`, `>`, `<=`, or `<` against "YYYY-MM-DD" or
"YYYY-MM-DD HH:mm", read as UTC, with an optional trailing `ORDER BY`
`lastmodified` or `created`. `created` is version 1's time and
`lastmodified` the latest version's, so a page edited again after a window
no longer matches a `lastmodified` bound on it. Anything else raises a loud
error, as JQL does.

JQL support in searchJiraIssuesUsingJql is a small, documented subset:
clauses joined by AND, each one of `project = KEY`, `status != NAME`,
`statusCategory != NAME` (and the `=` forms), `text ~ "words"` or
`summary ~ "words"` (substring match against summary+description),
`created` compared with `>=`, `>`, `<=`, `<`, or `=` against "YYYY-MM-DD" or
"YYYY-MM-DD HH:mm" (slashes also accepted), and `creator`, `reporter`, or
`assignee` with `=`, `!=`, `in (...)`, or `not in (...)` against account
IDs, `currentUser()`, or `EMPTY`, or with `is EMPTY` / `is not EMPTY`, with an optional trailing `ORDER BY` over `Rank`, `created`, `updated`,
`duedate`, or `key`, each `ASC` (the default) or `DESC`, comma-separated.
Anything else raises a loud error naming the unsupported construct rather
than silently matching nothing or everything -- the same fail-loud property
as the other stubs.

Created times: JQL date-times carry no time zone, and Jira reads them in the
searching account's profile time zone (JRACLOUD-81174), so the stub reads
them in the fixture's optional top-level "timeZone", or UTC without one, and
compares against each issue's "created", which carries its own offset. A
date with no time means midnight that day, so `created >= "2026-10-01" AND
created < "2026-10-02"` spans the whole day. User clauses match account IDs
only; an issue with no "creator" uses its "reporter".

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

import datetime
import difflib
import re
import zoneinfo

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


_CREATED_OPERATORS = (">=", "<=", ">", "<", "=")


def _parse_iso(value: str) -> datetime.datetime:
    """An ISO timestamp with offset, accepting a trailing Z."""
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_jql_datetime(value: str) -> datetime.datetime:
    """A JQL date or date-time, read in the account's time zone."""
    text = value.replace("/", "-")
    for layout in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            naive = datetime.datetime.strptime(text, layout)
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"jira-stub: unsupported JQL date {value!r} -- use YYYY-MM-DD or YYYY-MM-DD HH:mm")
    return naive.replace(tzinfo=zoneinfo.ZoneInfo(state.data.get("timeZone", "UTC")))


def _match_created(issue: dict, clause: str) -> bool:
    for operator in _CREATED_OPERATORS:
        value = _clause_value(clause, "created", operator)
        if value is None:
            continue
        actual = _parse_iso(issue["created"])
        bound = _parse_jql_datetime(value)
        return {
            ">=": actual >= bound, "<=": actual <= bound, ">": actual > bound,
            "<": actual < bound, "=": actual == bound,
        }[operator]
    raise ValueError(f"jira-stub: unsupported JQL clause {clause!r} (created supports >=, >, <=, <, =)")


def _user_values(raw: str) -> list[str]:
    """Account IDs from one value or an `in (...)` list, resolving currentUser()."""
    raw = raw.strip()
    if raw.startswith("(") and raw.endswith(")"):
        raw = raw[1:-1]
    items = [v.strip().strip('"\'') for v in raw.split(",") if v.strip()]
    me = (state.data.get("me") or {}).get("accountId")
    return [me if v.lower() == "currentuser()" else v for v in items]


def _match_user_field(issue: dict, clause: str, field: str) -> bool:
    person = issue.get(field) if field != "creator" else (issue.get("creator") or issue.get("reporter"))
    actual = (person or {}).get("accountId")
    rest = clause[len(field):].strip()
    lower = rest.lower()
    operators = (("not in", True), ("in", False), ("is not", True), ("is", False), ("!=", True), ("=", False))
    for operator, negate in operators:
        if not lower.startswith(operator):
            continue
        tail = rest[len(operator):].lstrip()
        if operator.endswith("in") and not tail.startswith("("):
            continue
        if operator.startswith("is") and tail.upper() != "EMPTY":
            continue
        values = _user_values(tail)
        hit = actual in values or (actual is None and any(v.upper() == "EMPTY" for v in values))
        return hit != negate
    raise ValueError(
        f"jira-stub: unsupported JQL clause {clause!r} "
        f"({field} supports =, !=, in, not in, is EMPTY, is not EMPTY)"
    )


def _clause_matches(issue: dict, clause: str) -> bool:
    c = clause.strip()
    lower = c.lower()
    if lower.startswith("project"):
        return _match_project(issue, c)
    for field in ("creator", "reporter", "assignee"):
        if lower.startswith(field):
            return _match_user_field(issue, c, field)
    if lower.startswith("created"):
        return _match_created(issue, c)
    for field in ("statuscategory", "status"):
        if lower.startswith(field):
            return _match_status_field(issue, c, field)
    for field in ("text", "summary"):
        if lower.startswith(field):
            return _match_text_field(issue, c, field)
    raise ValueError(
        f"jira-stub: unsupported JQL clause {clause!r} -- supported: project =, status =/!=, "
        "statusCategory =/!=, text ~, summary ~, created >=/>/<=/</=, creator/reporter/assignee "
        "=/!=/in/not in/is EMPTY, joined by AND, optional trailing ORDER BY"
    )


_ORDER_FIELDS = {
    "rank": lambda i: i.get("rank") or i.get("created") or "",
    "created": lambda i: i.get("created") or "",
    "updated": lambda i: i.get("updated") or "",
    "duedate": lambda i: i.get("duedate") or "",
    "key": lambda i: (i["project"], int(i["key"].rsplit("-", 1)[1])),
}


_ORDER_BY = " order by "


def _split_order_by(jql: str) -> tuple[str, str]:
    """The JQL's filter part and its ORDER BY terms, either possibly empty."""
    padded = f" {jql}"
    lower = padded.lower()
    if _ORDER_BY not in lower:
        return jql, ""
    at = lower.index(_ORDER_BY)
    return padded[:at].strip(), padded[at + len(_ORDER_BY):].strip()


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
    project =, status =/!=, statusCategory =/!=, text ~, summary ~,
    created >=/>/<=/</=, creator/reporter/assignee =/!=/in/not in/is EMPTY,
    joined
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


# --- Confluence search and version history --------------------------------

_CQL_OPERATORS = (">=", "<=", ">", "<")


def _page_versions(page: dict) -> list[dict]:
    """A page's versions, oldest first."""
    versions = page.get("versions") or [{
        "number": 1, "authorId": state.data.get("me", {}).get("accountId", ""),
        "createdAt": _STUB_NOW, "collaborators": [], "body": page.get("body", "")}]
    return sorted(versions, key=lambda v: v["number"])


def _content_type(page: dict) -> str:
    return "live_doc" if page.get("subType") == "live" else "page"


def _version_view(page: dict, version: dict) -> dict:
    return {"contentType": _content_type(page), "number": version["number"],
            "authorId": version["authorId"], "message": version.get("message", ""),
            "createdAt": version["createdAt"], "minorEdit": False}


def _get_page(content_id: str) -> dict:
    page = state.data.get("pages", {}).get(str(content_id))
    if page is None:
        raise ValueError(f"atlassian-stub: no Confluence content with id {content_id!r}")
    return page


def _get_version(page: dict, number: int) -> dict:
    for version in _page_versions(page):
        if version["number"] == int(number):
            return version
    raise ValueError(f"atlassian-stub: content {page['id']} has no version {number}")


def _parse_cql_datetime(value: str) -> datetime.datetime:
    text = value.replace("/", "-")
    for layout in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(text, layout).replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"atlassian-stub: unsupported CQL date {value!r} -- use YYYY-MM-DD or YYYY-MM-DD HH:mm")


def _split_cql_and(query: str) -> list[str]:
    """Split CQL on AND, in any letter case, only outside "quoted values",
    so `title ~ "bugs and fixes"` stays one clause."""
    clauses, buffer, in_quotes, index = [], "", False, 0
    while index < len(query):
        char = query[index]
        if char == '"':
            in_quotes = not in_quotes
        if not in_quotes and query[index:index + 5].lower() == " and ":
            clauses.append(buffer)
            buffer, index = "", index + 5
            continue
        buffer += char
        index += 1
    clauses.append(buffer)
    return [c.strip() for c in clauses if c.strip()]


def _split_cql_clause(clause: str) -> tuple[str, str, str]:
    """A clause's field, operator, and unquoted value, split at the first
    operator without regular expressions: `type in (page, live)` keeps its
    list in the value."""
    text = clause.strip()
    lower = text.lower()
    marks = [i for i in (lower.find(c) for c in "<>=~") if i >= 0]
    at_in = lower.find(" in ")
    if at_in >= 0 and (not marks or at_in < min(marks)):
        field, operator, value = text[:at_in], "in", text[at_in + 4:]
    elif marks:
        at = min(marks)
        operator = text[at:at + 2] if text[at:at + 2] in (">=", "<=") else text[at]
        field, value = text[:at], text[at + len(operator):]
    else:
        return lower, "", ""
    return field.strip().lower(), operator, value.strip().strip("()").strip().strip('"')


def _cql_clause_matches(page: dict, clause: str) -> bool:
    versions = _page_versions(page)
    field, operator, value = _split_cql_clause(clause)
    if field in ("contributor", "creator") and operator == "=":
        if field == "creator":
            return versions[0]["authorId"] == value
        return any(value == v["authorId"] or value in v.get("collaborators", []) for v in versions)
    if field in ("created", "lastmodified") and operator in _CQL_OPERATORS:
        actual = _parse_iso((versions[0] if field == "created" else versions[-1])["createdAt"])
        bound = _parse_cql_datetime(value)
        return {">=": actual >= bound, "<=": actual <= bound,
                ">": actual > bound, "<": actual < bound}[operator]
    if field == "type" and operator in ("=", "in"):
        wanted = {t.strip().strip('"').lower() for t in value.split(",")}
        kinds = {"page"} | ({"live"} if page.get("subType") == "live" else set())
        return bool(kinds & wanted)
    if field == "space" and operator == "=":
        return page.get("spaceKey", "").lower() == value.lower()
    if field in ("title", "text", "sitesearch") and operator == "~":
        # A case-insensitive substring match: title ~ reads the title alone;
        # text ~ and siteSearch ~ read the title, excerpt, and current body.
        haystack = page.get("title", "")
        if field != "title":
            haystack += " " + page.get("excerpt", "") + " " + page.get("body", "")
        return value.lower() in haystack.lower()
    raise ValueError(f"atlassian-stub: unsupported CQL clause {clause!r}")


def _search_result(page: dict) -> dict:
    latest = _page_versions(page)[-1]
    webui = page.get("webui") or f"/spaces/{page.get('spaceKey', 'ENG')}/pages/{page['id']}/{page['title'].replace(' ', '+')}"
    content = {"id": page["id"], "type": "page", "status": "current",
               "title": page["title"], "_links": {"webui": webui}}
    if page.get("subType"):
        content["subType"] = page["subType"]
    seconds = _parse_iso(latest["createdAt"]).astimezone(datetime.timezone.utc).replace(microsecond=0)
    return {"content": content, "title": page["title"], "excerpt": page.get("excerpt", ""),
            "url": webui, "resultGlobalContainer": {"title": page.get("space", "")},
            "entityType": "content",
            "lastModified": seconds.strftime("%Y-%m-%dT%H:%M:%S.000Z")}


@server.tool()
def searchConfluence(  # NOSONAR(S1542) camelCase = real MCP tool name
    cql: str,
    cloudId: str = "",
    limit: int = 25,
    start: int = 0,
) -> dict:
    """Search Confluence content with CQL (Confluence Query Language).
    Date-times in created and lastmodified take the form "YYYY-MM-DD HH:mm"
    and are read as UTC."""
    if cloudId:
        _check_cloud(cloudId)
    args = {"cql": cql, "cloudId": cloudId, "limit": limit, "start": start}
    query, order = _split_order_by(" ".join(cql.split()))
    clauses = _split_cql_and(query)
    try:
        pages = [p for p in state.data.get("pages", {}).values()
                 if all(_cql_clause_matches(p, c) for c in clauses)]
        if order:
            field, _, direction = order.partition(" ")
            index = 0 if field.lower() == "created" else -1
            if field.lower() not in ("created", "lastmodified"):
                raise ValueError(f"atlassian-stub: unsupported CQL ORDER BY {order!r}")
            pages.sort(key=lambda p: _parse_iso(_page_versions(p)[index]["createdAt"]),
                       reverse=direction.strip().lower() == "desc")
    except ValueError as error:
        # Logged before refusing, so a grader sees the attempt in the call log.
        state.log_call("searchConfluence", args, {"error": str(error)})
        raise
    window = pages[start:start + limit]
    result = {"data": {"results": [_search_result(p) for p in window],
                       "start": start, "limit": limit, "size": len(window), "totalSize": len(pages),
                       "_links": {"base": f"{state.data['cloud']['url']}/wiki"}}}
    state.log_call("searchConfluence", {"cql": cql, "cloudId": cloudId, "limit": limit, "start": start}, result)
    return result


@server.tool()
def listConfluenceContentVersions(  # NOSONAR(S1542) camelCase = real MCP tool name
    contentId: str,
    cloudId: str = "",
) -> dict:
    """List the versions of a Confluence page or live doc, newest first.
    Each version's createdAt is when its editing session started."""
    if cloudId:
        _check_cloud(cloudId)
    page = _get_page(contentId)
    result = {"data": {"results": [_version_view(page, v) for v in reversed(_page_versions(page))]}}
    state.log_call("listConfluenceContentVersions", {"contentId": contentId, "cloudId": cloudId}, result)
    return result


def _read_content_version(arguments: dict) -> dict:
    page = _get_page(arguments["contentId"])
    version = _get_version(page, arguments["versionNumber"])
    view = _version_view(page, version)
    view["prevVersion"] = version["number"] - 1 if version["number"] > 1 else None
    view["collaborators"] = version.get("collaborators") or [version["authorId"]]
    data = {"ok": True, "contentType": _content_type(page), "version": view}
    if arguments.get("content_format"):
        data["body"] = {"format": arguments["content_format"], "value": version.get("body", ""),
                        "lossyConversion": True, "lostFeatures": []}
    return {"data": data}


def _read_diff(arguments: dict) -> dict:
    page = _get_page(arguments["contentId"])
    old = _get_version(page, arguments["from_version"])
    new = _get_version(page, arguments["to_version"])
    latest = _page_versions(page)[-1]["number"]
    lines = list(difflib.unified_diff(
        old.get("body", "").splitlines(), new.get("body", "").splitlines(),
        fromfile=f"a/{page['id']}@v{old['number']}.md", tofile=f"b/{page['id']}@v{new['number']}.md",
        lineterm=""))
    additions = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
    status = lambda n: "current" if n == latest else "historical"  # noqa: E731
    return {"data": {"ok": True, "id": page["id"], "contentType": _content_type(page),
                     "from": {"version": old["number"], "status": status(old["number"])},
                     "to": {"version": new["number"], "status": status(new["number"])},
                     "diff": {"patch": "\n".join(lines) + ("\n" if lines else ""),
                              "additions": additions, "deletions": deletions,
                              "hunks": sum(1 for l in lines if l.startswith("@@")), "empty": not lines}}}


def _person(account_id: str) -> dict:
    user = next((u for u in state.data.get("users", []) if u["accountId"] == account_id), None)
    if user is None:
        return {"person": {"accountId": account_id}, "facets": {"identity": {"status": "not_found"}},
                "partial": True}
    identity = {"accountId": account_id, "name": user["displayName"],
                "email": user.get("emailAddress", ""), "accountStatus": "active"}
    return {"person": {"accountId": account_id, "name": user["displayName"]},
            "facets": {"identity": {"status": "complete", "data": identity}}, "partial": False}


def _read_people(arguments: dict) -> dict | list:
    identifiers = arguments["identifier"]
    if isinstance(identifiers, str):
        identifiers = [identifiers]
    if len(identifiers) > 10:
        raise ValueError("atlassian-stub: getPeopleInfo takes at most 10 identifiers per call")
    people = [_person(i) for i in identifiers]
    return people[0] if len(people) == 1 else people


_READS = {"getConfluenceContentVersion": _read_content_version,
          "diffConfluenceContentVersions": _read_diff,
          "getPeopleInfo": _read_people}


@server.tool()
def executeRead(  # NOSONAR(S1542) camelCase = real MCP tool name
    name: str,
    arguments: dict | None = None,
) -> dict | list:
    """Run a read-only Atlassian operation by name. Supported names:
    getConfluenceContentVersion (contentId, versionNumber, optional
    content_format: "markdown"), diffConfluenceContentVersions (contentId,
    from_version, to_version), and getPeopleInfo (identifier: up to 10
    account IDs)."""
    arguments = arguments or {}
    if name not in _READS:
        error = f"atlassian-stub: unsupported executeRead name {name!r}"
        state.log_call("executeRead", {"name": name, "arguments": arguments}, {"error": error})
        raise ValueError(error)
    result = _READS[name](arguments)
    state.log_call("executeRead", {"name": name, "arguments": arguments}, result)
    return result


if __name__ == "__main__":
    server.run(transport="stdio")
