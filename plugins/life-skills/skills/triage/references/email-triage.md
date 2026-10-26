# Email Triage

Everything specific to an email scope: how to fetch the corpus, and the Step 7b
decision tree that each thread walks. Read this when the scope is an inbox, a
Gmail label, a search query, or a set of threads. For any other scope it does
not apply.

## Fetching an email corpus (Step 2)

Follow the same MCP → skill → CLI → REST hierarchy Step 2 defines. The Gmail
MCP exposes the operations needed: `search_threads`, `get_thread`,
`list_labels`, `modify_thread_labels`, `archive_thread`, `create_draft`.
Marking read or unread is a label change: remove or add `UNREAD`. Use
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
   propose deleting it. A thread is noise on its own subject and snippet, not
   because it shares a sender with noise. Once the user decides one, SKILL.md
   Step 9b offers the same decision for the threads like it.
2. **2-minute rule?** If a reply or action can be completed in under two
   minutes and is ever going to be done, offer to draft it now. On a yes,
   draft it via `create_draft`: show the draft, confirm the wording, then
   leave it in the user's Gmail drafts for them to review and send. The
   Gmail MCP does not send; sending stays with the user.
3. **Reference only?** If the thread is purely informational and should be
   kept, propose the account's existing label that fits it (sift-email's
   rubric decides which, when there is one) and archiving out of the inbox.
   Search is the retrieval mechanism, not folder navigation.
4. **Action, > 2 minutes?** Capture the action somewhere durable: capture to
   Trello via the Step 7c flow as a card whose title is the action Step 6
   named, or keep it in Gmail the way the account already marks threads to
   act on (an existing label, a star, or left in the inbox). The preferences
   file may say what happens to the thread once it has a card (unstar it,
   archive it).
5. **Waiting for someone else?** The next move is the other person's, but the
   thread's action is still the user's: the check-in Step 6 named, saying who
   it is with, what it is about, and when. A date the thread gives (a
   promised reply, a deadline) sets when; with none, ask rather than pick one.
   Where the check-in is recorded follows the pattern the scope already uses,
   such as an existing waiting-for label or a Trello list
   ([determining-actions.md](determining-actions.md)); with no pattern, name
   the check-in and ask when and where to record it. The reply reads as the
   user's action, never as the other person's:

   ```
   Check-in:  check in with the landlord about the dishwasher repair
   When should I remind you to check in?
   ```
6. **Read later?** If the content is long-form and worth reading but not
   actionable now, propose the account's existing read-later label or star,
   if it has one, or leaving it in the inbox; ask when it has neither.

No branch marks a thread read, or unread, as a side effect: archiving leaves
the read state as it was unless the user asked (SKILL.md Step 9a). Always
confirm each label change, draft, read-state change, and archive before
writing, unless the user authorized it up front.

## Closing an email run

After the last thread, surface counts in the closing report:

```
Inbox processed: N threads
  Deleted:       X
  Replied (<2m): X
  Captured:      X (Trello: X, kept in Gmail: X)
  Check-ins:     X
  Read later:    X
  Reference:     X
  Marked read:   X
```

Labels are never created here. A label the account lacks is offered only
from a pattern across three or more threads (SKILL.md Step 9b).
