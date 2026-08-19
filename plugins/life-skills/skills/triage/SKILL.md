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

**An empty scope is a finished run.** If the confirmed scope turns out to hold
no items, report that and stop. Zero is a complete answer, not a failed search:
do not re-query the same scope a different way, and do not reach outside it —
archived mail, other lists, closed issues, the rest of the account — looking for
something to work on. Name what you searched, say it came back empty, and offer
to look elsewhere. Widening the scope needs the user to ask for it, exactly as
setting the scope did.

**Bounded-read rule for email:** never read full message bodies for the entire
scoped set up front. Fetch only metadata (subject, from, date, snippet, labels)
for the corpus. Read full bodies one thread at a time, only on items the user
agrees to act on or that require a body read to classify.

**Scope Confirmation block:** every run records its scope in this block and
shows it to the user before any item-level detail is fetched:

```
Scope:     <board / project / inbox / specific item>
Source:    user request | user reply | sole candidate from discovery
Confirmed: yes | pending
```

- When the user named the target (in the original request or in a reply to
  the scope question), Source is that message and Confirmed is `yes`.
- When the user did not specify what to process, the first reply is the
  scope question above and nothing else. Capability discovery waits until
  the user answers; do not survey targets first and infer from what exists.
- If the user's answer still leaves the target open ("whatever I have",
  "you pick"), run capability discovery then. If exactly one candidate
  exists, proceed with the block showing `Source: sole candidate from
  discovery` and `Confirmed: pending`: reading and auditing are allowed,
  but the Step 8 proposal must lead with this block and ask the user to
  confirm the scope, and nothing is applied while it is pending. If more
  than one candidate exists, list them and ask; audit none of them.
- Only a user message flips Confirmed to `yes`. The assistant never sets it
  on its own authority, and "there was only one candidate" is a Source, not
  a confirmation.

**Capability discovery:** once scope is named (or on the open-answer path
above), survey what is available in the current session. Check which MCP
tools are loaded, which skills are available, and which CLI tools respond to
`command -v <tool>`. Use the best available option for the platform implied
by the scope. If the platform is ambiguous, ask. Discovery informs *how* to
fetch, never *what* the scope is.

---

## Step 0.5: Assess Scale and Agree on Pace

Before fetching full detail, get a lightweight count and title-only pass across
the scoped set.

Under ~15 items, go straight into per-item processing. At 15+, use the
title-only pass to spot grouping signals (sender, label, list, component,
keyword) and to agree a pace with the user: Step 8's proposal-and-confirm
summary runs once per batch of ~10 rather than once at the very end. That
changes only how often Step 8 runs, never whether a change is confirmed before
it is applied.

This pass never substitutes for individual review. Every item still runs the
full per-item loop (Steps 2 through 8).
[references/sizing-and-tiers.md](references/sizing-and-tiers.md) has the
wording to propose batching with.

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

**Capture for each item during this corpus pass:** title/subject, a short
description/body snippet, type, status/list/folder, assignee(s)/recipients,
labels/tags, due date, start date, priority, creation date, and last-updated
date. This listing-level detail is enough for Step 0.5 sizing and Step 2's
context/size assessment. Defer heavier detail (effort estimate, linked items,
attachments, embedded URLs, comments with dates, and external links) to the
Step 2.0 refresh immediately before each item's individual review, so each
item gets fetched in full once per run, not twice.

For an email scope, read
[references/email-triage.md](references/email-triage.md) before fetching. It
covers the Gmail operations to use, and how the corpus pass stays inside Step
0's bounded-read rule.

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

### 2a-2c. Context, size, and enrichment tier

Classify the item on two axes and let them pick a tier:

- **Work context** — personal, professional, or mixed.
- **Task size** — small (one action, under a day), medium (a few steps, 1-5
  days), or large/project (multi-week, multi-phase, multiple people).

Personal + small selects **Tier 1** (title clarity, and a due date only if it
is time-sensitive). Professional small/medium, or personal medium/large,
selects **Tier 2** (title, description outcome, labels, assignee, priority,
due date). Professional + large selects **Tier 3** (Tier 2 plus phases,
external links, and an effort estimate).

When in doubt, start at a lower tier. It is always better to under-enrich and
ask than to impose structure the user didn't want.

[references/sizing-and-tiers.md](references/sizing-and-tiers.md) has the signal
tables for each axis and the full tier table — read it whenever an item's
context or size is not obvious at a glance.

---

## Step 3: Scan for Similar and Related Items

**Professional boards and projects.** For personal boards with small tasks,
skip this step unless the user has asked you to look for duplicates.

Before auditing the individual item, search the same board or project for items
sharing key terms with its title and description, and classify what comes back:
direct overlap is a probable duplicate to merge, close or link; partial overlap
is a link; a sequential dependency is a backlog ordering suggestion; no overlap
is passed over silently. Confirm every proposed link or merge before applying.

[references/gathering-context.md](references/gathering-context.md) has the
search scoping per platform, the fields to request, and the relationship table
in full.

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
the description. If the title is a noun phrase, a question, or too vague to act
on, propose a rewrite and confirm before changing it. **Only propose the title
once**, in the final change summary (Step 8), not earlier.

### Description

A description should answer: what needs to be done, why it matters, what done
looks like, and any constraints. If key parts are missing, suggest additions in
plain language that fits the context. Confirm before adding anything.

### Labels / Tags

Propose labels that will help find the item later, specific over generic when
both apply. Always present suggested labels and ask for confirmation. Never add
without approval.

For all three: how much of this an item actually needs, and what good looks
like for a personal chore versus a professional bug versus a project, is in
[references/field-guidance.md](references/field-guidance.md) — worked examples
per context, plus the de-duplication check for descriptions built by a
forwarding or capture automation. Read it before proposing a rewrite.

### Assignee / Recipient

If unassigned and the item is active, ask who should own it. On a personal
board or project where the user is the only member, leave the field unassigned
and do not raise it — assigning the sole member to their own item records
nothing. Skip the field, not the question: do not read "no need to ask" as
"assign it yourself". For an outgoing email follow-up captured as a
`Waiting For`, the implicit owner is the recipient, not the user.

### Due Date

If no due date is set and the item is active (not backlog/icebox), ask whether
there is a target date. Do not invent a date.

### Priority (Professional items only)

On a personal item, leave priority unset and do not raise it. Skip the field,
not the question: a due date that conveys urgency is not a reason to set
priority as well. Position in the list is what orders a personal board, and a
lone High on a two-item personal project ranks nothing against anything.

On a professional item, if priority is not set, suggest one based on the
description, labels, and any blocking relationships. Confirm before applying.

### Effort / Story Points (Tier 3 professional items only)

If the project uses estimation and the item is unestimated, ask for an estimate
or suggest one based on comparable items. Confirm before applying.

---

## Step 4b: Email-Specific Triage Workflow

**Email scope only.** Skip this step for a board, project, or single item.

Once the corpus is enumerated and per-item context and size are read (Steps 2
and 3), every thread walks a six-way decision tree before Step 5: delete,
reply now under the 2-minute rule, file as reference, capture as an action,
mark as waiting on someone else, or park as a long read. The run then closes
with a processed-count summary.

Read [references/email-triage.md](references/email-triage.md) for the tree in
full — the order the branches are tested in, what each one writes, the count
block's format, and the label bootstrap. Do not work from this summary alone;
the branch order is what makes the tree deterministic, and it is in that file.

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
   - **Description:** required, not optional. Include a link back to the source
     item being triaged (Trello card URL, Jira issue URL, or Gmail thread URL
     or message ID). A card that does not name its source has lost the thing
     that made it a capture. When one source yields several cards, write the
     description on every one of them — the back-link belongs on the cards
     themselves, not only in the summary you send the user, and never claim in
     that summary that a card links back unless you put the link on the card.
   - **Labels and due date:** propose based on the source item's context.
4. **A capture is not a license to edit the source.** The item you captured
   *from* gets triaged on its own merits by the normal per-item loop and no
   other way. In particular, do not rewrite its description to strip out the
   text you just extracted: capturing an action elsewhere does not make the
   original wording wrong, and an edit made for tidiness destroys the record of
   what the item actually said. If the capture is worth recording on the source,
   add a comment — additive, attributable, and it leaves the original intact.
5. **Always confirm before creating or editing.** Never auto-write.

For email scope, capturing to Trello replaces the in-Gmail `Action` label
path for items that are likely to outlive a single inbox review. The
discriminator is durability: keep it as a Gmail `Action` label if the next
action is "reply to this thread"; capture to Trello if the action lives
outside email or will take longer than a few days.

---

## Step 5: Gather Context from Existing Links

**Only when the item carries links.** An item with no embedded URLs, no
attachments and no linked items has nothing to gather; go straight to Step 7.

Before searching for anything new, follow every URL the item already carries —
in the description, the comments, the attachments, the web links, or for email
the thread body. Linked content is the most direct source of context available
and should inform every suggestion made downstream: title rewrites, description
drafts, label choices, status comments. Anything that cannot be fetched is
reported as unresolved rather than described as if it had been read.

## Step 6: Search for Additional External Content

**Tier 2 and Tier 3 only.** Skip for Tier 1 personal tasks.

Search Slack, GitHub, Drive, email and Confluence for material related to the
item that nobody has linked yet, and propose adding what you find as a link.
Step 6a proposes a grouping label when a recurring theme surfaces across the
set.

Read [references/gathering-context.md](references/gathering-context.md) for
both steps in full: which URLs to collect, the domain-to-tool table for
fetching them past an auth wall, the local `references/` directory check, how
gathered context feeds each field, resolving auto-captured placeholder text,
and the search order for Step 6.

## Step 7: Staleness Check

**Only for items that have gone quiet.** Items in a Done or equivalent closed
status are exempt outright.

Calculate the days since real activity — a comment, a field update, a status
change, or for email the last message in the thread. Under a week, note it and
move on. Past a week, ask whether to draft a status comment. Past three weeks,
ask the same and offer the stall interview. Treat a suspiciously identical
timestamp shared across many items as a bulk import rather than real activity,
and fall back to content signals.

Read [references/staleness-and-stalls.md](references/staleness-and-stalls.md)
for the exact thresholds, what a status comment has to establish before it is
worth posting, the Jira ADF posting format, and the five-question stall
interview for items past 30 days with no progress.

## Step 8: Present Proposed Changes and Apply

**Scope check first:** if Step 0's Scope Confirmation block is still
`Confirmed: pending`, open this summary with that block and ask the user to
confirm the scope before anything else in it. Nothing is applied while the
block reads pending, no matter how routine the proposals look.

Collect proposals into a summary and ask for confirmation before applying
anything. For sets processed in batches (Step 0.5), present and confirm this
summary once per batch of ~10 items; otherwise present it once for the whole
run. Do not present the same change in multiple places. Items with no
proposed changes still appear in the summary, flagged as "No changes — looks
complete. Mark reviewed?" rather than being dropped.

Every item named in the summary is a hyperlink to itself: use the item's own
web URL as returned by the platform (a Trello card's `url`/`shortUrl`, a Jira
issue's browse URL, a Gmail thread's URL), so the heading reads
`Proposed changes for [Book flights to Austin](https://trello.com/c/abc123):`
rather than a bare title or a bare `PROJ-123`. The same applies to any card,
issue, or thread mentioned elsewhere in the summary, including newly created
Trello cards (Step 4c) and linked items. Only ever use a URL the platform
actually returned — if an item's URL is unavailable, say so and name the item
in plain text rather than constructing one.

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

The procedure above is built from GTD (capture, clarify, organize, reflect,
engage), the 2-minute rule, Kanban flow and WIP limits, LEAN's just-enough
structure, and the reference-versus-action split. When a judgment call comes up
that the steps do not settle, these are what to reason from — most often: state
a next action or the item is not active, do anything under two minutes now, and
never impose more structure than the work justifies.

[references/methodology.md](references/methodology.md) has each one in full.

## Quality Rules

- Review every item individually, even ones that already look complete or
  well-formed. A high-quality item still gets a checkpoint ("no changes
  needed, mark as reviewed or complete?") rather than being silently passed
  over. The user decides whether an item needs a change, not you by omission.
- Never apply a change without explicit user confirmation.
- Never invent facts, dates, names, or descriptions. Ask if unknown.
- Refer to every card, issue, or thread by a hyperlink to the item itself,
  never a bare title or key, and never a URL the platform did not return.
- Always show the full draft of any comment, email, or new Trello card before
  writing it.
- Preserve the user's voice in any drafted text.
- One question at a time during the stall interview.
- Propose each change once, in the final Step 8 summary, not earlier.
- If scope is ambiguous, stop and ask before proceeding.
- If the scope is empty, that is the answer. Report it and stop; do not widen
  past it looking for work.
- When the user did not specify what to process, the first reply is the
  Step 0 scope question alone, before any discovery. Any later
  sole-candidate proceed happens read-only under a Scope Confirmation block
  marked pending: nothing is written while it is pending, only a user
  message can set Confirmed to yes, and the Step 8 summary opens with that
  block asking for confirmation whenever it is still pending.
- For email, never read full bodies of the entire corpus up front. Honor the
  bounded-read rule in Step 0.

---

## References

Bundled, each linked from the step that needs it — read on demand, not up front:
[email-triage](references/email-triage.md) (Step 4b and email fetching),
[gathering-context](references/gathering-context.md) (Steps 3, 5, 6),
[staleness-and-stalls](references/staleness-and-stalls.md) (Step 7, 7a, 7b),
[field-guidance](references/field-guidance.md) (title, description and label
calibration), [sizing-and-tiers](references/sizing-and-tiers.md) (Steps 0.5 and
2a-2c), [methodology](references/methodology.md) (GTD, Kanban, LEAN).

External:

- [Trello REST API](https://developer.atlassian.com/cloud/trello/rest/)
- [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Gmail API](https://developers.google.com/gmail/api)
- [GTD: Getting Email Under Control (David Allen)](https://gettingthingsdone.com/wp-content/uploads/2014/10/GettingEmail.pdf)
