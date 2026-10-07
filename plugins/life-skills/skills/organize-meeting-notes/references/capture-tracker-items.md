# Capturing Tracker Items Created During the Meeting

Read this in Step 1b when a ticket tracker (Jira, Trello, or another task
tool) is reachable. It finds the work items and cards participants created
during the meeting, which the raw notes often do not mention.

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
  relates to when proposing it. An item that shares no subject with the
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
present it with that gap stated and ask the user whether an attendee created
it. Never assume a creator from the item's content or from who owns the
board. Leave out items an integration or automation created when the tool
identifies them as such.

## Reporting

When presenting tracker items, found or empty, open with one line per
tracker in this shape, before any finding:

`<Tracker>: searched items created <start> to <end + 15 minutes> (<search used>); found <count> by or assigned to attendees.`

For example: `Jira: searched items created 2:00 PM to 3:00 PM (created
2026-10-01); found 3 by or assigned to attendees.` Then list each item with
its key or link, summary, status, who created it, who it is assigned to,
and its creation time. Mark each one created after the meeting ended, with
the meeting content it relates to. List each item left out because it fell
after the end and did not relate to the meeting, so the user can overrule
that call.

## Where They Go

Propose each item; the user decides what gets in.

- **Notes**: place the item beside the discussion it came from, using the
  Step 5 tracked work item format (`[KEY-123](...): <summary> (<status>)`).
  An item with no matching note follows the Step 5 unanchored enrichment
  rule.
- **Action items**: when the item is a task, it also becomes a Step 7 action
  item linked to it, led by its assignee, or its creator when unassigned.
  Ask for a due date the item does not carry, as Step 7 does for any action
  item.
- **No duplicates**: when a confirmed action item matches a captured item,
  link the captured item and do not create a Trello card for it. Ask the
  user when it is unclear whether the two are the same work.
