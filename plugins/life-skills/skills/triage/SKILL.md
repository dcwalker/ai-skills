---
name: triage
description: >
  Process and triage a backlog of items, Trello cards, Jira work items, or email
  threads, so each has clear, actionable metadata, a well-formed next step, and
  is filed where it belongs. Use when the user wants to audit a card, ticket,
  board, project backlog, or email inbox for completeness and actionability.
  Also triggers for: "process my backlog", "process my inbox", "triage my
  email", "triage my backlog", "can you look at this card/ticket", "review my
  backlog", "clean up my board", "clean up my inbox", "this issue has been
  sitting for a while", "help me triage", "what's in my inbox".
metadata:
  category: life-skills
---

# Triage

Review and enrich one or more items so that each has clear, actionable metadata
and a well-formed next step. The depth and language of the review should match
the nature and size of the work. A quick personal chore needs very different
treatment than a complex engineering feature or a flagged email. Draw on GTD
(capture, clarify, organize, reflect, engage), Kanban (flow, WIP), and LEAN
(eliminate waste, maximize value) principles throughout.

The core GTD framing: every input source is an in-box, every in-box is a
processing station and not a storage bin, and the goal of a processing run is
to empty the scoped set by making a clear decision about each item, not by
finishing all the work behind the items.

---

## Step 0: Establish Scope

If the user did not specify what to process, ask:

> "What would you like to process? You can share a card URL, an issue key, a
> board name, a project key, an email inbox, a Gmail label or folder, or just
> describe what you're working on."

Do not proceed until scope is clear. Accept any of:

- A Trello card URL or short link (e.g. `https://trello.com/c/abc123`)
- A Trello board name or board ID
- A Jira issue key (e.g. `PROJ-123`) or URL
- A Jira project key or JQL filter
- An email inbox (default: Gmail `in:inbox`)
- A Gmail label, folder, search query, or specific thread URLs

**Default for email:** if the user says "process my email," "triage my inbox,"
or similar without qualifying the scope, assume `in:inbox`. Do not expand to
all mail.

**Bounded-read rule for email:** never read full message bodies for the entire
scoped set up front. Fetch only metadata (subject, from, date, snippet, labels)
for the corpus. Read full bodies one thread at a time, only on items the user
agrees to act on or that require a body read to classify.

**Capability discovery:** Before fetching, survey what is available in the
current session. Check which MCP tools are loaded, which skills are available,
and which CLI tools respond to `command -v <tool>`. Use the best available
option for the platform implied by the scope. If the platform is ambiguous,
ask.

---

## Step 0.5: Assess Scale and Agree on Pace

Before fetching full detail, get a lightweight count and title-only pass
across the scoped set.

- Under ~15 items: proceed straight into per-item processing (Step 1 onward).
- 15+ items: do a lightweight first pass on titles/subjects and any obvious
  grouping signal (sender, label, list, component, keyword). Use it to flag
  candidate theme-grouping labels (see Step 6a) and to agree with the user on
  how often to run Step 8's proposal-and-confirm summary: once per batch of
  ~10 items, rather than once at the very end, e.g. "This set has 42 items.
  I'll still review each one individually and confirm every change before
  applying it, that's the point, but I'll summarize and confirm proposals in
  batches of 10 instead of one giant summary at the end. Sound right?" This
  changes only how often Step 8 runs, never whether a change gets confirmed
  before it's applied.
- This pass never substitutes for individual review. Every item still runs the
  full per-item loop (Steps 2 through 8).

---

## Step 1: Fetch the Item(s)

Use the best available tool for the platform. In order of preference:

1. **MCP** — if an MCP for the platform is loaded in this session, use it.
   Common examples: Atlassian MCP for Jira/Confluence, a Trello MCP if present,
   a Gmail MCP for email.
2. **Skill** — if a relevant skill is available (e.g. `twg` for Jira project
   or backlog scans, `trello-tools` skills for Trello), load and invoke it.
3. **CLI** — if a CLI for the platform is installed (`command -v <tool>`),
   invoke it. Pass flags to request all fields. For Trello, `trello-tools`
   provides `--view`, `--search`, `--create-card`, and related commands.
4. **REST / WebFetch** — fall back to a direct API call if nothing else is
   available. Jira: `GET /rest/api/3/issue/{key}?fields=*all`. Trello:
   `GET https://api.trello.com/1/cards/{id}?fields=all&actions=all`. Gmail:
   the Gmail REST API.

For broader Jira project or backlog scans, load the `twg` skill if available.

### Email-specific fetching

For email scope, follow the same MCP → skill → CLI → REST hierarchy. The Gmail
MCP exposes the operations needed: `search_threads`, `get_thread`,
`list_labels`, `modify_thread_labels`, `archive_thread`, `create_draft`. Use
`search_threads` with the scope query (e.g. `in:inbox`) to enumerate the
corpus, then fetch metadata only. Defer `get_thread` (full body) until needed
per the bounded-read rule.

**Capture for each item during this corpus pass:** title/subject, a short
description/body snippet, type, status/list/folder, assignee(s)/recipients,
labels/tags, due date, start date, priority, creation date, and last-updated
date. This listing-level detail is enough for Step 0.5 sizing and Step 2's
context/size assessment. Defer heavier detail (effort estimate, linked items,
attachments, embedded URLs, comments with dates, and external links) to the
Step 2.0 refresh immediately before each item's individual review, so each
item gets fetched in full once per run, not twice.

---

## Step 2: Refresh, Read Context, and Size

### 2.0 Per-Item Refresh

Step 1's corpus pass is listing-level only (see "Capture for each item" in
Step 1), to keep the up-front fetch cheap on large sets. Immediately before
starting an item's individual pass (2a onward), fetch that item fresh and in
full from source: this is the single point where full detail (effort
estimate, linked items, attachments, embedded URLs, comments with dates, and
external links) gets captured, not a repeat of Step 1. Fetching fresh here
also protects against staleness, since time passes while working through a
set and other people or automations can change items in the meantime.

If the fresh fetch shows the item no longer matches the original scope (it's
been completed, closed, reassigned away from the user, moved out of the
inbox/filter, or deleted), skip the remaining steps for that item, note why in
the final summary, and move to the next item.

Before auditing anything, make two quick assessments. These shape every
suggestion you make for the rest of the run.

### 2a. Work context

| Context | Signals |
|---|---|
| **Personal** | Personal board, no team members, items like "buy groceries", "plan trip", "call dentist"; personal email account |
| **Professional** | Team board/project, issue types like Bug/Story/Epic, sprint context, business terminology; work email account |
| **Mixed** | Personal productivity board used for work tasks, or a team board with personal to-dos mixed in; a single inbox that receives both |

### 2b. Task size

| Size | Signals |
|---|---|
| **Small** | Single clear action, completable in under a day, no dependencies, obvious done state. For email, a single reply or a single follow-up. |
| **Medium** | Multiple steps or sub-tasks, 1–5 days of effort, may have a dependency or two |
| **Large / Project** | Multi-week or multi-phase effort, has sub-tasks or should have them, involves multiple people or systems |

### 2c. Select enrichment tier

Use the context and size to select the right enrichment level. The goal is
*just enough structure to move the item forward*, no more.

| Tier | When | What to enrich |
|---|---|---|
| **1 — Lightweight** | Personal + Small, or any pure personal quick-task, or a short email that needs only a reply or a delete | Title/subject clarity, assignee (if shared), due date (if time-sensitive), maybe a brief note |
| **2 — Standard** | Professional + Small/Medium, or Personal + Medium/Large, or an email that needs to be captured as an action | Title, description outcome, labels, assignee, priority, due date |
| **3 — Full** | Professional + Large, or any item that is clearly a project or initiative | Everything in Tier 2, plus phases/sub-tasks, external links, and effort estimate |

When in doubt, start at a lower tier. It is always better to under-enrich and
ask than to impose structure the user didn't want.

---

## Step 3: Scan for Similar and Related Items

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

---

## Step 4: Audit Metadata

Audit the fields appropriate to the item's tier. For each missing or unclear
field, apply this decision rule:

| Confidence | Action |
|---|---|
| High — obvious from context | State the intended value; give the user a chance to object |
| Medium — reasonable inference | Suggest the value and ask for confirmation |
| Low — genuinely unclear | Ask before proposing anything |

### Title / Subject

A good title is action-oriented and specific enough to act on without reading
the description. Calibrate the phrasing to the context:

- **Personal task:** Use natural language. "Book flights for Austin trip" is
  better than "Flight booking" or "Book flights (acceptance criteria: ...)".
- **Professional task/bug:** Lead with the outcome. "Fix unexpected logout after
  30 min inactivity on mobile" beats "auth bug".
- **Project/initiative:** State the end goal. "Launch self-serve billing portal
  for SMB customers" beats "billing portal".
- **Email captured as an action:** When converting an email into a tracked
  action (a Trello card, a Jira issue, or a stored email action label), set
  the title or subject line to the next action verb, not the original email
  subject. "Reply to Sue with Q3 forecast" beats "FW: Q3 numbers".

If the title is a noun phrase, a question, or too vague to act on, propose a
rewrite and confirm before changing it. **Only propose the title once**, in the
final change summary (Step 8), not earlier.

For personal items with no description to draw from, ask a brief question
rather than guessing.

### Description

A description should answer: what needs to be done, why it matters, what done
looks like, and any constraints. Calibrate to the context:

- **Personal small task:** A single sentence is often enough. No need for formal
  sections or headers.
- **Personal project:** Key details relevant to the domain. For a trip, that
  means destination, dates, budget, who's going. For a home project, scope,
  materials, and timeline. Write as plain prose, no section headers.
- **Professional task or bug (Tier 2):** A short paragraph covering what needs
  doing, why it matters, and what a completed state looks like, written as
  prose, not as named sections. Only use structured headers (e.g. "Acceptance
  criteria") for Tier 3 items where the complexity genuinely warrants them.
- **Professional initiative/epic (Tier 3):** Full context including stakeholders,
  success metrics, and known constraints. Structured sections are appropriate here.

If key parts are missing, suggest additions in plain language that fits the
context. Confirm before adding anything.

Capture and forwarding automations often duplicate content, for example a
cleaned summary followed by a repeated "original message" block, or a
forwarded quote chain. Check for this and propose a de-duplicated version
rather than preserving redundant copies.

### Labels / Tags

Propose labels that will help find the item later. Calibrate to context:

- **Personal:** Simple tags like "travel", "home", "health", "finance".
- **Professional:** Domain ("auth", "billing"), type ("bug", "feature",
  "tech-debt"), and specifics ("mobile", "ios", "android"). Prefer specific
  over generic when both apply.
- **Email:** Use plain label names with no prefix character. The core action
  labels are `Action`, `Waiting For`, and optionally `Read-Review` and
  `To-Print`. Reference labels are topical (person, project, domain).

Always present suggested labels and ask for confirmation. Never add without
approval.

### Assignee / Recipient

If unassigned and the item is active, ask who should own it. For personal
boards where the user is the only member, skip this. For an outgoing email
follow-up captured as a `Waiting For`, the implicit owner is the recipient,
not the user.

### Due Date

If no due date is set and the item is active (not backlog/icebox), ask whether
there is a target date. Do not invent a date.

### Priority (Professional items only)

If not set, suggest a priority based on the description, labels, and any
blocking relationships. Confirm before applying. Skip for personal tasks.
Priority on a personal board is usually managed by list position.

### Effort / Story Points (Tier 3 professional items only)

If the project uses estimation and the item is unestimated, ask for an estimate
or suggest one based on comparable items. Confirm before applying.

---

## Step 4b: Email-Specific Triage Workflow

For email scope, after the corpus is enumerated and per-item context and size
are read (Steps 2 and 3), walk each thread through this decision tree before
moving on to Step 5. The tree applies GTD email principles directly.

For each thread, decide in this order:

1. **Delete?** If the thread has no future value as either action or reference,
   propose deleting it. When the corpus is large, offer to group by sender and
   bulk-delete obvious noise.
2. **2-minute rule?** If a reply or action can be completed in under two
   minutes and is ever going to be done, draft it now via `create_draft`. Show
   the draft, confirm the wording, then leave it in the user's Gmail drafts
   for them to review and send. The Gmail MCP does not send; sending stays
   with the user. Do not defer.
3. **Reference only?** If the thread is purely informational and should be
   kept, propose applying a topical reference label and archiving out of the
   inbox. Use a single flat label list, not nested labels. Search is the
   retrieval mechanism, not folder navigation.
4. **Action, > 2 minutes?** Capture the action somewhere durable:
   - Apply the `Action` label and edit the subject of a stored copy (or note
     the action verb in a comment), **or**
   - Capture to Trello via the Step 4c flow below as a card whose title is
     the next action verb. Either way, then archive the thread out of the
     inbox.
5. **Waiting for someone else?** Apply the `Waiting For` label and archive.
   The label, not the inbox, is the reminder surface.
6. **Read-review later?** If the content is long-form and worth reading but
   not actionable now, apply `Read-Review` and archive.

Always confirm each label change, draft, and archive before writing.

After walking the corpus, surface counts:

```
Inbox processed: N threads
  Deleted:       X
  Replied (<2m): X
  Captured:      X (Trello: X, action label: X)
  Waiting For:   X
  Read-Review:   X
  Reference:     X
```

Remind the user that `Action` and `Waiting For` labels are only useful if
reviewed regularly, and suggest a review cadence if the user does not already
have one.

If any of the `Action`, `Waiting For`, `Read-Review`, or `To-Print` labels do
not yet exist in the user's Gmail account (check via `list_labels`), propose
creating them and confirm before doing so.

---

## Step 4c: Capture Follow-Ups to Trello

During any triage run, whenever a discovered action is complex (multi-step),
cannot be done right now, or is explicitly for-later, offer to record it as a
Trello todo so it is not lost.

Apply this flow:

1. **Search first.** Look for an existing card that already covers the action.
   Tool hierarchy:
   1. **MCP** — Trello MCP `search_trello` or equivalent.
   2. **CLI** — `trello-tools --search "QUERY" --search-board-id "$BOARD_ID"`.
   3. **REST** — Trello search API.
2. **If a card exists:** verify its title or description names the *next*
   concrete action. If it does not, propose a rewrite of the title or an
   addition to the description and confirm before applying.
3. **If no card exists:** offer to create one.
   - **Board:** the single open Trello board, resolved via the same hierarchy
     (`get_boards` → `trello-tools --view board` → REST). If there are
     multiple open boards, ask the user which one.
   - **List:** the user's default inbox/triage list on that board. If unknown,
     ask.
   - **Title:** lead with the next action verb (Step 4 "Title" rules apply).
   - **Description:** include a link back to the source item being triaged
     (Trello card URL, Jira issue URL, or Gmail thread URL or message ID).
   - **Labels and due date:** propose based on the source item's context.
4. **Always confirm before creating or editing.** Never auto-write.

For email scope, capturing to Trello replaces the in-Gmail `Action` label
path for items that are likely to outlive a single inbox review. The
discriminator is durability: keep it as a Gmail `Action` label if the next
action is "reply to this thread"; capture to Trello if the action lives
outside email or will take longer than a few days.

---

## Step 5: Gather Context from Existing Links

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

### 5e. Resolve Auto-Captured Content

Some items are created by an automated capture from another system (a chat
integration, a form submission, an email-to-ticket rule) rather than typed
directly. Signs include placeholder tokens (a user ID instead of a name),
terse fragments lifted out of context ("just ask her to add"), or a
captured-by/integration signature. Before drafting a title or description
rewrite, identify the true source and intent, resolving placeholders with real
names or context where discoverable, rather than propagating them into the
cleaned-up version.

---

## Step 6: Search for Additional External Content

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

### 6a. Propose Theme Groupings

If the Step 0.5 scan or the accumulated per-item audits surface a recurring
theme not yet captured by an existing label or tag, propose a new grouping
label and name the items it would apply to. Confirm before creating or
applying it.

---

## Step 7: Staleness Check

Calculate the number of days since the last activity (comment, field update,
status change, or for email, the last message in the thread). Items in a
"Done" or equivalent closed status are exempt.

| Age with no activity | Action |
|---|---|
| 3–7 days | Note it; no action required |
| 8–21 days | Ask: "No updates in N days, want me to draft a status comment or follow-up?" |
| 22+ days | Ask the same; if no clear progress, also offer the stall interview (Step 7b) |

Before trusting the last-activity timestamp, confirm it reflects real
activity. A bulk import, sync, or migration can stamp many items with an
identical timestamp that has nothing to do with when the item was actually
last touched. If several items in the set share a suspiciously identical
timestamp, treat it as unreliable and fall back to content signals instead:
dates mentioned in the description, comment dates, or linked PR/doc activity.

### Step 7a: Draft a Status Comment or Follow-Up

Search recent activity on the item and any linked content (PRs, docs, Slack,
prior email threads) to find what has actually happened. Draft a comment or
email that:

- States current status factually
- Notes any blockers or dependencies
- Proposes a specific next action

Show the full draft and get explicit approval before posting or saving.

Use the best available tool to post the comment or save the draft (MCP →
skill → CLI → REST), following the same hierarchy as Step 1. For Jira, if
posting via REST, use ADF format (not plain text):

```bash
curl -s -X POST \
  -u "${ATLASSIAN_USER_EMAIL}:${ATLASSIAN_USER_API_KEY}" \
  -H "Content-Type: application/json" \
  "https://YOUR-SITE.atlassian.net/rest/api/3/issue/{key}/comment" \
  -d '{"body": <ADF doc>}'
```

For Gmail follow-ups, use `create_draft` to save a draft. The Gmail MCP does
not send; surface the saved draft to the user so they can review and send it
themselves in Gmail.

---

## Step 7b: Stall Interview (30+ Days, No Progress)

If an item has been open for more than 30 days with no meaningful progress,
and the user wants to unblock it, initiate a structured interview using the
`conduct-interview` skill. The goal is one immediately actionable next step.

Frame the interview around:

1. What was the original intent of this item?
2. What has been tried? What was the result?
3. What is blocking progress right now?
4. Can this be broken into smaller pieces? What would the first piece be?
5. Is this still valuable, or should it be closed/deferred?

Apply LEAN thinking: if the item has no owner, no recent interest, and no
dependency, closing or deferring it is often the right answer.

After the interview, produce:

- A rewritten title if needed
- Child tasks or subtasks for each phase, or a Trello card capture via Step 4c
- A recommended status or list assignment for the parent
- A comment summarizing the review

Confirm all changes before applying.

---

## Step 8: Present Proposed Changes and Apply

Collect proposals into a summary and ask for confirmation before applying
anything. For sets processed in batches (Step 0.5), present and confirm this
summary once per batch of ~10 items; otherwise present it once for the whole
run. Do not present the same change in multiple places. Items with no
proposed changes still appear in the summary, flagged as "No changes — looks
complete. Mark reviewed?" rather than being dropped.

```
Proposed changes for [ITEM TITLE] ([KEY or URL]):

Title:        [old] → [new]
Description:  [what you'd add or change]
Labels:       add [x, y]; remove [z]
Assignee:     [name]
Due date:     [date]
Priority:     [value]
Links:        add "[item title]" ([source])
Comment:      [preview]
Sub-tasks:    [list]
Todos:        capture to Trello board "[board]" → list "[list]"
              - [title 1]
              - [title 2]
Email:        archive after labeling / save draft reply (preview) / delete
```

Ask: "Shall I apply these?" Wait for an affirmative before writing anything.

Before applying any status-changing action (closing, archiving, marking
complete), confirm how the platform's status model and automations behave, for
example whether "closed" means archived versus done, or whether marking an
item complete can trigger a side effect like auto-archiving. Getting this
wrong is hard to notice after the fact.

Apply in this order:

1. Title / summary
2. Description additions
3. Labels, priority, assignee, due date
4. Issue links and web links
5. Child tasks / subtasks
6. Trello todo captures (Step 4c)
7. Status comment or saved Gmail draft (user sends from Gmail)
8. Email archive / delete

After applying, re-fetch the item (or refresh the inbox count) and confirm the
changes landed.

---

## Step 9: Check for New Arrivals

Re-run the original Step 0 scope query (same board, filter, label, or inbox
search) and compare against the set of items processed in this run. If new
items now match the scope that weren't part of the original corpus, report the
count and ask whether the user wants to process them in this session or a
follow-up run.

---

## Methodology Notes

**GTD** — Every item needs a clear next action. If you cannot state one, the
item is not ready to be in an active status. Pull it back to inbox/backlog.
Every input source is an in-box, and every in-box is a processing station,
not a storage bin. The goal of a processing run is to empty the scoped set by
deciding about each item, not by finishing all the work behind the items.

**The 2-minute rule** — Applies universally, not just to email. If processing
an item surfaces an action that takes under two minutes and is ever going to
be done, do it now (reply, comment, set the label, archive). Anything longer
gets captured as a tracked action.

**Kanban** — An item in an active column with no assignee, no due date, and no
recent activity is unmanaged WIP. Assign it and move it forward, or pull it
out of the active flow.

**LEAN** — Don't create more structure than the work justifies. A two-minute
task does not need a scope document. Impose just enough process to keep things
moving, and no more.

**Reference vs. action** — Keep actionable and non-actionable items in
separate places. Reference items belong in a topical label or folder, never
in the inbox. Action reminders belong in a dedicated action surface (Trello,
Jira, or the `Action` and `Waiting For` Gmail labels), never mixed in with
reference material.

---

## Quality Rules

- Review every item individually, even ones that already look complete or
  well-formed. A high-quality item still gets a checkpoint ("no changes
  needed, mark as reviewed or complete?") rather than being silently passed
  over. The user decides whether an item needs a change, not you by omission.
- Never apply a change without explicit user confirmation.
- Never invent facts, dates, names, or descriptions. Ask if unknown.
- Always show the full draft of any comment, email, or new Trello card before
  writing it.
- Preserve the user's voice in any drafted text.
- One question at a time during the stall interview.
- Propose each change once, in the final Step 8 summary, not earlier.
- If scope is ambiguous, stop and ask before proceeding.
- For email, never read full bodies of the entire corpus up front. Honor the
  bounded-read rule in Step 0.

---

## References

- [Trello REST API](https://developer.atlassian.com/cloud/trello/rest/)
- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Gmail API](https://developers.google.com/gmail/api)
- [GTD: Getting Email Under Control (David Allen)](https://gettingthingsdone.com/wp-content/uploads/2014/10/GettingEmail.pdf)
