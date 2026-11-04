# Capturing Tracker Items Created During the Meeting

Read this in Step 1b when a ticket tracker (Jira, Trello, or another task
tool) or Confluence is reachable. It finds the work items and cards
participants created during the meeting, and the Confluence pages they
created or edited, which the raw notes often do not mention.

## Which Items Count

An item counts when an attendee created it, or anyone created it and it is
assigned to an attendee. Use the Step 3 attendee list, matched by email or
account rather than display name alone.

The window runs from the meeting's actual start to 15 minutes after its
actual end:

- **Created between the actual start and end**: include it whether or not it
  relates to the meeting. Like a chat side conversation, it shows what the
  attendees were doing.
- **Created in the 15 minutes after the end**: include it only when it
  relates directly to something discussed in the meeting (a topic in the
  notes, an agenda item, a decision, or an action item). Name the content it
  relates to when including it. An item that shares no subject with the
  meeting is left out, not offered as a question. Ask the user only when the
  item plausibly connects to the meeting but the connection is uncertain;
  never include it on a guess.
- **Created before the start, or more than 15 minutes after the end**: leave
  it out.

Use actual times, not scheduled ones, as with chat. Compare creation times in
the meeting's time zone: take it from the meeting details, the calendar, or
the chat profile. When none gives it, ask the user once before sorting items
into the window; a tracker's UTC times cannot be placed without it.

## Finding Them

Search by creation date first, then filter by time and person, the same way
chat is read by window before any keyword search. A keyword search misses
the item that matters most, because a task created mid-meeting rarely
repeats the meeting's words.

- **Jira**: search with JQL bounded by `created` only, covering the
  meeting's date, for example `created >= "2026-10-01" AND created <
  "2026-10-02" ORDER BY created ASC`. JQL date-times carry no time zone and
  are read in the account's Jira profile time zone, so bound the search by
  whole days and filter on each result's `created` timestamp, which carries
  its offset. Request the `creator`, `reporter`, and `assignee` fields.
  Jira records both a creator and a reporter; use the creator, and the
  reporter only when the creator is not returned.
- **Trello**: search for cards created since the meeting date (`created:N`,
  where N covers the days from the meeting to today). The search reports a
  creation date only; take each card's exact creation time from its ID,
  whose first 8 hexadecimal characters are a Unix timestamp in seconds.
  Convert it with a tool (for example `date -r $((16#<8 hex characters>))`
  on macOS, or `date -d @$((16#<8 hex characters>))` on Linux) rather than
  by hand.
  Trello's search has no operator for a card's creator, so use `@member`
  searches only to find cards assigned to an attendee.

Page through the results until they run out. When a tracker tool cannot
search by creation time, say so and ask the user how to proceed rather than
falling back to keywords.

When the tool does not show who created an item, or who it is assigned to,
look for it in another source (a chat message announcing the item, the
item's activity, the user's other notes). When none shows it, state that gap
and ask the user whether an attendee created it. Never assume a creator from the item's content or from who owns the
board. Leave out items an integration or automation created when the tool
identifies them as such.

## Reporting

In the Step 8 report, found or empty, open the tracker findings with one
line per tracker in this shape, before any finding:

`<Tracker>: searched items created <start> to <end + 15 minutes> (<search used>); found <count> by or assigned to attendees.`

For example: `Jira: searched items created 2:00 PM to 3:00 PM (created
2026-10-01); found 3 by or assigned to attendees.` Then list each item with
its key or link, summary, status, who created it, who it is assigned to,
and its creation time. Mark each one created after the meeting ended, with
the meeting content it relates to. List each item left out because it fell
after the end and did not relate to the meeting, so the user can overrule
that call.

## Confluence Pages

A page or live doc (Confluence's always-editable page type, such as the
meeting page Loom creates) counts when an attendee created it or edited it
within the same window as tracker items: from the actual start to 15
minutes after the actual end, with the same rule for the 15 minutes after
the end. A page reaches the notes this way even when nobody shared its link.

**Finding them**: search with CQL for each attendee's account ID (look it
up by email first) as a contributor, bounded from the day before the
meeting's date rather than by its times, for example for a meeting on
Mar 12, 2026: `contributor = "<account ID>" and lastmodified >=
"2026-03-11"`. A later edit replaces `lastmodified`, so a page edited again
after the window no longer matches a bound on the window itself. CQL reads
dates and `"YYYY-MM-DD HH:mm"` as UTC, so a bound on the meeting's own date
can miss an edit made late in the evening west of UTC; starting a day
early covers it, and version history then places each edit. Page through
the results until they run out.

**Placing an edit in the window**: for each result, list the page's
versions. Each version records when its editing session started; reading a
version gives every account that edited during that session. A version
whose start falls in the window places an edit by those accounts in it; a
page whose first version falls in it was created in it. A session is one
version however long it ran (a live doc saves one about 15 minutes after
the last edit), so the notes can say that an attendee edited a page during
the meeting, but never when a line in it was written. To say what changed,
diff the in-window version against the one before it.

**Loom meeting pages**: Loom creates its page a few minutes before the
meeting and adds its recap a few minutes after it, and both versions carry
the organizer's account ID. A Loom page counts only when an attendee other
than the organizer edited it in the window. When only the organizer's
account appears, leave it out as Loom's own edits and say so in the
report.

**Reporting**: open the Confluence findings with one line in the tracker
line's shape, before any finding:

`Confluence: searched pages edited <start> to <end + 15 minutes> (<search used>); found <count> created or edited by attendees.`

Then list each page with its link, title, who created or edited it, and the
version time, marking each one created rather than edited. List each page
left out, and why (edited only outside the window, or only Loom's edits),
so the user can overrule that call.

## Where They Go

Include each item that counts, without asking; the report lists them all.

- **Notes**: place the item beside the discussion it came from, using the
  Step 5 tracked work item format (`[KEY-123](...): <summary> (<status>)`).
  A Confluence page goes in as a Markdown link with who created or edited
  it during the meeting and what the edit holds. An item with no matching
  note follows the Step 5 unanchored enrichment rule.
- **Action items**: when the item is a task, it also becomes a Step 7 action
  item linked to it, led by its assignee, or its creator when unassigned.
  Find a due date the item does not carry as Step 7 does for any action
  item.
- **No duplicates**: when an action item matches a captured item,
  link the captured item and do not create a task for it. Ask the
  user when it is unclear whether the two are the same work.
