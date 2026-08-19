# Email Triage

Everything specific to an email scope: how to fetch the corpus, and the Step 4b
decision tree that each thread walks. Read this when the scope is an inbox, a
Gmail label, a search query, or a set of threads. For any other scope it does
not apply.

## Fetching an email corpus (Step 1)

Follow the same MCP → skill → CLI → REST hierarchy Step 1 defines. The Gmail
MCP exposes the operations needed: `search_threads`, `get_thread`,
`list_labels`, `modify_thread_labels`, `archive_thread`, `create_draft`. Use
`search_threads` with the scope query (e.g. `in:inbox`) to enumerate the
corpus, then fetch metadata only. Defer `get_thread` (full body) until needed,
per Step 0's bounded-read rule.

**Capture for each item during this corpus pass:** title/subject, a short
description/body snippet, type, status/list/folder, assignee(s)/recipients,
labels/tags, due date, start date, priority, creation date, and last-updated
date. This listing-level detail is enough for Step 0.5 sizing and Step 2's
context/size assessment. Defer heavier detail (effort estimate, linked items,
attachments, embedded URLs, comments with dates, and external links) to the
Step 2.0 refresh immediately before each item's individual review, so each
item gets fetched in full once per run, not twice.

## The Step 4b decision tree

After the corpus is enumerated and per-item context and size are read (Steps 2
and 3), walk each thread through this tree before moving on to Step 5. The tree
applies GTD email principles directly.

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
   - Capture to Trello via the Step 4c flow as a card whose title is the next
     action verb. Either way, then archive the thread out of the inbox.
5. **Waiting for someone else?** Apply the `Waiting For` label and archive.
   The label, not the inbox, is the reminder surface.
6. **Read-review later?** If the content is long-form and worth reading but
   not actionable now, apply `Read-Review` and archive.

Always confirm each label change, draft, and archive before writing.

## Closing an email run

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
