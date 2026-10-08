# Email Triage

Everything specific to an email scope: how to fetch the corpus, and the Step 7b
decision tree that each thread walks. Read this when the scope is an inbox, a
Gmail label, a search query, or a set of threads. For any other scope it does
not apply.

## Fetching an email corpus (Step 2)

Follow the same MCP → skill → CLI → REST hierarchy Step 2 defines. The Gmail
MCP exposes the operations needed: `search_threads`, `get_thread`,
`list_labels`, `modify_thread_labels`, `archive_thread`, `create_draft`. Use
`search_threads` with the scope query (e.g. `in:inbox`) to enumerate the
corpus, then fetch metadata only. Defer `get_thread` (full body) until needed,
per Step 0's bounded-read rule.

**Capture for each item during this corpus pass:** title/subject, a short
description/body snippet, type, status/list/folder, assignee(s)/recipients,
labels/tags, due date, start date, priority, creation date, and last-updated
date, plus whether the thread carries `STARRED` or `IMPORTANT` in its
`labelIds`. This listing-level detail is enough for Step 1's sizing and order
and Step 3's context/size assessment. Defer heavier detail (effort estimate,
linked items, attachments, embedded URLs, comments with dates, and external
links) to the Step 3.0 refresh immediately before each item's individual
review, so each item gets fetched in full once per run, not twice.

`search_threads` returns the newest thread first. That is the listing's order,
not the inbox's processing order: work the threads Starred or Important first,
then oldest first (Step 1b), which usually means reading the listing from the
bottom up.

**A thread that points elsewhere needs its body.** When the snippet says the
substance is behind a link (a statement is ready, a document was shared, a
message is waiting in a portal), the bounded-read rule counts the thread as
one that needs a body read to classify. Read it with `get_thread`, and follow
its link under Step 5a before the tree below decides the thread. Step 5a's
list of links never to open applies in full: an unsubscribe, confirm, or
one-time link in the body is named for the user, not opened.

## The Step 7b decision tree

After the corpus is enumerated, per-item context and size are read (Steps 3
and 4), and Step 6 has named the thread's action, walk each thread through this
tree. The tree applies GTD email principles directly.

For each thread, decide in this order:

1. **Delete?** If the thread has no future value as either action or reference,
   propose deleting it. When the corpus is large, offer to group by sender and
   delete obvious noise as one batch action (SKILL.md Step 1a). A thread
   joins the batch only when its own subject and snippet show it is noise,
   not because it shares a sender with noise. Threads a batch action leaves
   in the inbox, such as after a batch label, still walk this tree
   individually.
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
   - Capture to Trello via the Step 7c flow as a card whose title is the
     action Step 6 named. Either way, then archive the thread out of the inbox.
5. **Waiting for someone else?** Apply the `Waiting For` label and archive.
   The label, not the inbox, is the reminder surface. The next move is the
   other person's, but the thread's action is still the user's: the check-in
   Step 6 named, saying who it is with, what it is about, and when. A date the
   thread gives (a promised reply, a deadline) sets when; with none, ask
   rather than pick one. Where the check-in is recorded follows the pattern
   the scope already uses
   ([determining-actions.md](determining-actions.md)); with no pattern, name
   the check-in in the summary and ask when and where to record it. The
   entry reads as the user's action, never as the other person's:

   ```
   Waiting For:  check in with the landlord about the dishwasher repair;
                 when should I remind you?
   ```
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
