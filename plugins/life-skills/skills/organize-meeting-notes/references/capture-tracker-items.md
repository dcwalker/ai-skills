# Capturing Tracker Items Created During the Meeting

Read this in Step 1b when a ticket tracker, task tool, or wiki is
reachable. It finds the work items and tasks participants created during
the meeting, and the wiki pages they created or edited, which the raw notes
often do not mention. The examples name common products only to make a
step concrete; translate each step into the reachable tool's own
operations.

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
into the window; a tracker's UTC times cannot be placed without it. Get the
window's UTC bounds, including the 15 minutes after the end, from
`python3 <skill-dir>/scripts/meeting_times.py window --start "YYYY-MM-DD
HH:MM" --end "HH:MM" --tz <IANA zone> --extend-end 15` rather than
converting by hand.

## Finding Them

Search by creation date first, then filter by time and person, the same way
chat is read by window before any keyword search. A keyword search misses
the item that matters most, because a task created mid-meeting rarely
repeats the meeting's words.

- Search by the item's creation date, covering the meeting's date, and
  sort by creation time. A tracker that reads date-only bounds in the
  account's own time zone (Jira's JQL does) can miss items near midnight,
  so bound the search by whole days and filter on each result's own
  creation timestamp, which carries its offset (for example in Jira:
  `created >= "2026-10-01" AND created < "2026-10-02" ORDER BY created
  ASC`).
- Request who created each item and who it is assigned to. When the tool
  records both a creator and a reporter, use the creator, and the reporter
  only when the creator is not returned.
- When the search reports a creation date only, take each item's exact
  creation time from another field the tool returns, and convert any
  timestamp with a tool rather than by hand.

Page through the results until they run out. When a tracker tool cannot
search by creation time, say so and ask the user how to proceed rather than
falling back to keywords.

When the tool does not show who created an item, or who it is assigned to,
look for it in another source (a chat message announcing the item, the
item's activity, the user's other notes). When none shows it, state that gap
and ask the user whether an attendee created it. Never assume a creator from
the item's content or from who owns the board or project. Leave out items an integration or automation created when the tool
identifies them as such.

## Reporting

In the Step 8 report, list the findings, never the search itself (no line
naming the window or the query used). List each item with its key or link, summary, status, who created it, who it is assigned to,
and its creation time. Mark each one created after the meeting ended, with
the meeting content it relates to. List each item left out because it fell
after the end and did not relate to the meeting, so the user can overrule
that call.

## Wiki Pages

A page or live doc (an always-editable page, such as the meeting page a
meeting recorder creates) counts when an attendee created it or edited it
within the same window as tracker items: from the actual start to 15
minutes after the actual end, with the same rule for the 15 minutes after
the end. A page reaches the notes this way even when nobody shared its link.

**Finding them**: search for pages each attendee's account (look it up by
email first) contributed to, bounded from the day before the meeting's
date rather than by its times. For example, in Confluence's CQL, for a
meeting on Mar 12, 2026: `contributor = "<account ID>" and lastmodified >=
"2026-03-11"`. A later edit replaces the last-modified date, so a page
edited again after the window no longer matches a bound on the window
itself. A wiki that reads date bounds as UTC (CQL does) can miss an edit
made late in the evening west of UTC; starting a day early covers it, and
version history then places each edit. Page through
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

**Meeting-recorder pages**: a meeting recorder (Loom, for example) creates
its page a few minutes before the meeting and adds its recap a few minutes
after it, and both versions carry the organizer's account ID. Such a page
counts only when an attendee other than the organizer edited it in the
window. When only the organizer's account appears, leave it out as the
recorder's own edits and say so in the report.

**Reporting**: list the findings, never the search itself. List each page with its link, title, who created or edited it, and the
version time, marking each one created rather than edited. List each page
left out, and why (edited only outside the window, or only the recorder's edits),
so the user can overrule that call.

## Where They Go

Include each item that counts, without asking; the report lists them all.

- **Notes**: place the item beside the discussion it came from, using the
  Step 5 tracked work item format (`[KEY-123](...): <summary> (<status>)`).
  A wiki page goes in as a Markdown link with who created or edited
  it during the meeting and what the edit holds. An item with no matching
  note follows the Step 5 unanchored enrichment rule.
- **Action items**: when the item is a task, it also becomes a Step 7 action
  item linked to it, led by its assignee, or its creator when unassigned.
  Find a due date the item does not carry as Step 7 does for any action
  item.
- **No duplicates**: when an action item matches a captured item,
  link the captured item and do not create a task for it. Ask the
  user when it is unclear whether the two are the same work.
