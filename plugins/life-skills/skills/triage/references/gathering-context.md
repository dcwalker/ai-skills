# Gathering Context

Steps 3, 5 and 6 in full: scanning for items related to this one, following
the links it already carries, and searching for content it does not. Read this
when looking for duplicates on a shared board, when an item has embedded URLs,
attachments or linked items, or when a Tier 2/3 item warrants a search for
material nobody has linked yet. A personal small task with no links skips all
three.

## Step 3: Scan for similar and related items

Before auditing the individual item, look for duplicates and candidates to
link or merge. This step matters most for professional boards/projects.

For personal boards with small tasks, skip this step unless the user has
asked you to look for duplicates.

Use the same tool hierarchy from Step 1. Search for items that share key terms
from the title and description. For Jira, scope the search to the same project
with `statusCategory != Done`. For Trello, scope to the same board. For email,
search prior threads with the same subject or correspondent. Limit results to
20 and request at minimum: title/summary, status, and assignee.

| Relationship | Action |
|---|---|
| Direct overlap (same work) | Present as probable duplicate; ask whether to merge, close one, or link |
| Partial overlap (related work) | Suggest linking ("Relates to" or "Blocks/Blocked by") |
| Sequential dependency | Suggest ordering in the backlog |
| No overlap | Proceed silently |

Confirm every proposed link or merge before applying.

## Step 5: Gather context from existing links

Before searching for new content, extract and follow every URL already embedded
in the item, description, comments, attachments, and web links, or for email,
the thread body. These are the most direct source of context and should inform
every suggestion you make downstream (title rewrites, description drafts,
label choices, status comments).

### 5a. Extract URLs

Collect all URLs from:

- Description body (inline links, bare URLs, and Markdown links)
- Each comment
- Attachments list
- Remote/web links already attached to the item
- For email: the message body. This is the point at which it is appropriate to
  read the full body for items still on the action path.

### 5b. Fetch each URL

For each URL, attempt access in this order:

1. **WebFetch first** — try a plain HTTP fetch. If it returns useful content,
   read it and move on.
2. **MCP fallback** — if WebFetch fails or returns an auth/login wall, use the
   appropriate authenticated tool based on the URL domain:

| Domain | Tool |
|---|---|
| `*.atlassian.net/wiki` / Confluence | `getConfluencePage` (Atlassian MCP) |
| `*.atlassian.net/browse` / Jira | `getJiraIssue` (Atlassian MCP) |
| `docs.google.com` / `drive.google.com` | `read_file_content` or `download_file_content` (Google Drive MCP) |
| `github.com/*/pull/*` | `gh pr view <url>` |
| `github.com/*/issues/*` | `gh issue view <url>` |
| `app.slack.com` / Slack message links | `slack_read_thread` or `slack_read_channel` (Slack MCP) |
| `mail.google.com` / Gmail | `get_thread` (Gmail MCP) |

If no MCP is available for a domain and WebFetch fails, note the URL as
unresolved and flag it for the user.

Some linked content has no extraction path with any available tool, such as
recorded video, whiteboard/canvas tools, or images without OCR. Note these as
unresolved rather than implying their content was read.

### 5c. Check local references directories

Look for a `references/` directory in two locations:

```bash
ls ./references/    # project root (current working directory)
ls ~/references/    # home directory
```

If either exists, scan the filenames for anything relevant to the item being
processed, matching the domain, component, team, or keywords from the title
and description. Read any relevant files and carry their content forward as
background context, the same way you would use content fetched from a URL.

Common things to look for: glossaries, naming conventions, architecture notes,
team ownership docs, workflow guides, decision records, or any domain reference
that would inform your suggestions.

### 5d. Use what you find

Integrate all gathered context, from URLs and local references, into your
triage. Specifically:

- Use it to improve the title rewrite (does the linked doc name the real outcome?)
- Use it to fill description gaps (does a linked spec answer what/why/done?)
- Use it to suggest labels (does a linked PR or reference doc name a component or team?)
- Use it to draft a status comment (does a linked PR or doc show recent progress?)
- Note any context that changes your read of the item's priority or staleness

### 5e. Resolve auto-captured content

Some items are created by an automated capture from another system (a chat
integration, a form submission, an email-to-ticket rule) rather than typed
directly. Signs include placeholder tokens (a user ID instead of a name),
terse fragments lifted out of context ("just ask her to add"), or a
captured-by/integration signature. Before drafting a title or description
rewrite, identify the true source and intent, resolving placeholders with real
names or context where discoverable, rather than propagating them into the
cleaned-up version.

## Step 6: Search for additional external content

For **Tier 2 and Tier 3** items, also search for relevant content not yet
linked. Skip for Tier 1 personal tasks.

**Search in this order:**

1. **Slack** — conversations mentioning the item title, issue key, or key terms
2. **GitHub** — PRs, issues, or commits that reference the item
   ```bash
   gh search prs "KEYWORD or issue key" --state all --limit 10
   ```
3. **Google Drive / Docs** — documents matching the item or linked from its description
4. **Email / Gmail** — threads related to the item title or key
5. **Confluence / wiki** — pages that reference the item (use `search-confluence` skill)

For every item found, propose adding it as a link. Confirm before adding.

### 6a. Propose theme groupings

If the Step 0.5 scan or the accumulated per-item audits surface a recurring
theme not yet captured by an existing label or tag, propose a new grouping
label and name the items it would apply to. Confirm before creating or
applying it.
