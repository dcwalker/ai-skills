---
name: create-task
description: Write a clear, actionable task, reminder, to-do, or action item in the Getting Things Done style, with a short glanceable title, the outcome, the contexts it needs (a place, a time window, a person), a due date only for a hard deadline, links to related work and its source, and the resources that make it quick to finish (URLs, phone numbers, addresses, names), in whatever format fits (a labeled block, prose, a checklist, Markdown, an outline, or an email with the title as its subject), then offer to file it in the user's tracker. Use whenever the user wants to add, capture, jot down, or create a task, reminder, to-do, follow-up, or action item, in any tool (Trello, Apple Reminders, Things, Todoist, Jira, a GitHub issue, a notes file), or asks to rewrite one so it is clearer, even when they just say "remind me to", "add a card for", "make a to-do", or "don't let me forget". Also the rulebook other skills, such as triage and organize-meeting-notes, follow when they write an item's title, description, owner, and dates, including a meeting's action items. Not for filing a bug report or feature request with a template of its own (use create-github-issue), and not for planning a whole project.
metadata:
  category: life-skills
---

# Create Task

Turn something the user needs to do into a task that tells them, in a
glance, what to do next, where and when it can happen, and everything they
need to finish it without hunting. Getting Things Done (GTD) is the
philosophy: a task is a single, concrete next action the user can do, kept
in a trusted system and organized by the context it needs.

A task is read far more often than it is written. It is scanned in a list
among dozens of others, on a phone, in the second before the user decides
what to do next. Every rule below serves that moment: the title has to land
in a split second, and the notes have to make the work quick once the user
picks it up.

## Step 1: Make sure it is an action

Name the next action as something the user does. Requests often arrive as
something else: a topic ("Garage"), an event ("Meeting moved to Thursday"),
another person's task ("Vendor to send quote"), or a whole project ("Plan the
reunion"). None of those is an action. Ask what the user does about it, and
write that.

| The user says | The task |
|---|---|
| "Prescription's ready" | Pick up the prescription at the pharmacy |
| "Can you send me the slides?" (from Priya) | Send the slides to Priya |
| "The landlord is fixing the dishwasher" | Check in with the landlord about the dishwasher repair |
| "Plan the reunion" | Pick three dates for the reunion and send them to the family |

Three kinds of action come up, and each is written a little differently:

- **Now.** Something to do at the next opportunity, with no particular time
  or place. If it takes under two minutes and you can help do it in this
  conversation (a short reply, a quick lookup), offer that ("Want me to
  draft that reply now?") and do it only on a yes. Otherwise it becomes a
  task.
- **At a time or place.** Tied to a date, a deadline, an appointment, a time
  window, or a location. Step 3 records the time and the place.
- **Check-in.** The next move is someone else's: a reply, a quote, a repair,
  a review. The user's action is to check in with that person about that
  thing. Write it out ("Check in with the landlord about the dishwasher
  repair"), never as the other person's task and never as "waiting".

A project (more than one action to reach the outcome) gets its next action
as the task, with the outcome in the notes. The later steps go in its notes
too, not on tasks of their own: one task per project, even when the steps
happen in different places, because only the next action can be done now.
When the user wants every step captured, list them, but the title is still
the first thing to do.

**Split a request that needs different contexts into separate tasks.** This
is for separate actions the user asked for together, not for a project's
steps, which stay on the project's one task. A
task is picked up where its context is: at the store, at the computer, on
the phone, with Sam. One task that says "call the landlord, then buy paint
at the hardware store" sits on a list where half of it can never be done,
so the user either skips it or has to reread it every time. Give each
context its own task, each with its own verb-first title and context, and
note in each how they connect ("after the landlord says yes"). When one
has to happen before another, say which comes first, and record the later
one's start condition the way Step 3 records a start date. Steps that
happen in the same place at the same sitting stay one task: "Buy paint,
rollers, and tape at the hardware store" is one trip, so it is one task,
with the items in the notes when the list is long.

Something with no action at all is not a task: it is reference (keep it
somewhere it can be found), someday (park it), or nothing. Say which instead
of forcing it into a to-do, and don't offer a to-do about keeping it ("Save
the code in the password manager"): say where it could live, and stop. Something already done is not a task either: a
decision made, a conversation held, or a ticket filed during the meeting
that produced the list is a record of what happened, and needs no question.

**The action belongs to its owner.** A task on the user's own list is the
user's action, so a move that is someone else's becomes the user's check-in.
A shared list is different: a meeting's action items, or a list for a team,
holds each person's own commitments, so each task is its owner's action
("Lena Fischer: Publish the Q4 on-call schedule"), and the user's check-in on
it belongs on the user's own list, if anywhere.

Writing the task is the job; doing it is not. When the user says what needs
doing ("I need to research flights to Denver"), capture that as the task and
do not start the research. Do the work only when the user asks for it in so
many words, or when a quick look of under two minutes makes the task itself
better (Step 4).

## Step 2: Write the title

The title is the whole task for most readers most of the time. It:

- **Leads with a verb** and names one concrete action: "Call", "Email",
  "Buy", "Book", "Renew", "Check in with". Not a noun phrase ("Car
  registration"), not a question ("Dentist?"), and not a vague verb that
  hides the real one ("Deal with taxes", "Follow up", "Handle insurance").
- **Is short enough to read in a glance.** Aim for about eight words or
  fewer, and well under the width of a phone screen. Cut articles and
  filler before cutting meaning. Details belong in the notes.
- **Is specific enough to act on without opening the notes.** Name the
  object and, when it matters, the person or place: "Renew the car
  registration online", "Pick up the dry cleaning on Main St".
- **Keeps the place when it is where the action happens** ("at the
  pharmacy", "at the leasing office"), unless the user's tool records places
  another way (Step 3).
- **Names who and what for a check-in:** "Check in with Sam about the Q3
  quote".

Calibrate to the setting:

- **Personal:** natural language. "Book flights for the Austin trip" beats
  "Flight booking".
- **Professional task or bug:** lead with the outcome. "Fix logout after 30
  minutes idle on mobile" beats "auth bug".
- **Captured from an email or message:** the next action, not the subject
  line. "Reply to Sue with the Q3 forecast" beats "FW: Q3 numbers".

## Step 3: Record what it needs to happen

### Outcome

Say what done looks like when the title alone doesn't: "Done when the new
plates are on the car", "Done when Sam has confirmed the Thursday time". One
sentence is usually enough for a personal task. A professional task gets a
short paragraph: what, why it matters, and what a finished state looks like,
written as prose. A large initiative or epic gets full context: who has a
stake in it, how success is measured, and the known constraints, and that is
the only place formal sections such as "Acceptance criteria" belong.

### Flexibility

Leave the user room. Say the outcome and the real constraints, not a method
they did not choose: "Get a quote for gutter cleaning" leaves the vendor open,
"Call Acme Gutters for a quote" does not, so write the second only when the
user named Acme. Add a constraint only when it is real (a budget, a vendor
the user picked, a size), and say where it came from when that isn't obvious.

### Contexts

GTD sorts tasks by what has to be true to do them, so the user can see
everything they could do right now, where they are, with what they have.
Note every context that applies, and only the ones that do:

- **Place:** where it must happen (home, the office, the hardware store,
  downtown, a computer, a phone).
- **Time window:** when it can happen, beyond a date: business hours,
  weekdays only, when the office or store is open (give the hours when you
  have them), daylight, before school pickup, a season.
- **Person:** who it needs, for an agenda item to raise with someone, a call,
  or something that needs another person present.
- **Combinations:** when several are needed together, note all of them
  ("At the bank, weekdays 9 to 5, with Jordan to co-sign"), and when one of
  several will do, say so ("By phone or in person").

Record a context the way the user's tool and system already do: a context
label or tag such as `@errands` or `@phone`, a Reminders location or time
alert, a list, or a line in the notes. Use the labels the system already has;
never invent a label for one task. With no system to follow, write contexts
as a short line in the notes.

### Owner

A task on the user's own list needs no owner. A task someone else owns, or
any task on a shared list, names its owner by full name, first in the line
when the list mixes owners. Take the owner from what was said or written
("I'll take that", an assignee in the tracker); look in the connected
sources when the notes don't say. Never guess one: when nothing settles who
took it, ask an open question ("Who owns this?") without proposing a name,
and leave the owner off if no one knows.

### Dates

A due date marks a hard deadline, not a date it would be nice to be done
by. Set one only when the task has a hard deadline: a date the task or its
sources state, or one that clearly follows from them. A stated deadline or
expiry is the due date itself. A deadline that follows from an event is the
event's date, or the day before when the work can't happen on the day
itself: packing for a trip that launches early on Jan 1 is due Dec 31. When
the user asks for a due date, use the timing they give; when they ask
without giving one, ask when.

A check-in's date is the day the other person promised to act ("I'll send it
by Thursday"), when they named one; with no promise, ask when to check in.
An appointment fixed at a set time keeps that time. A soft target ("hoping to
finish by Friday") is neither: it goes in the notes, not the due date. A
commitment made to others ("I'll publish it by Friday", said in a meeting)
is a deadline: it is the date someone is now counting on.

A date stated for something else is not this action's due date. When a
meeting says the old system shuts down on March 1, the action "migrate the
reports" is due March 1 only if the meeting tied that date to the migration
itself. Never derive a date from a dependency ("after the migration") either.

Otherwise, leave the date empty and do not raise it. Do not ask whether
there is a target date: a soft date adds a question the user has to decline,
and one set by mistake has to be found and removed later. The one exception
is a task that clearly hangs on a fixed event whose date you can't find (a
gift for a birthday): ask for that event's date.

A date the task can't start before (a renewal window that opens in March, a
call that has to wait until the office reopens) is a start or defer date,
not a due date. Use the tool's start, defer, or reminder field when it has
one, and the notes when it doesn't.

Never invent a date. A relative date ("next Friday") resolves against the
date of the message or meeting that says it. Keep the date in the source's
own words and add the calendar date when those words could mean more than
one ("by Friday (Aug 28, 2026)"). Write a weekday beside a date only after
checking it with a calendar tool (`date` or `cal`, for example); weekdays
worked out in your head are often wrong, and a wrong one makes the date
ambiguous. When you can't check, give the date alone.

When the user says what today is, or that the meeting or message was today,
that date is today, even if a system clock disagrees: resolve against it,
don't argue with it, and don't call a date passed by the clock's reckoning. A
date that has already passed by the user's today does not cancel the task:
keep it, say the date has passed, and let the user decide.

## Step 4: Make it quick to finish

### Resources

Include whatever would save the user a search when they sit down to do it:
the URL of the portal or form, the phone number, the address, the person's
full name and how to reach them, the order, account, or confirmation number,
the business hours, the price or quote. A task whose action happens
somewhere specific ("renew it online", "call the office") is not complete
without the means to do it.

When one of those is missing and a source already connected in this
conversation would likely have it (the email that prompted the task, the
user's files, a page the user linked), take a quick look, under two minutes,
and add what you find. Say where each one came from. Never guess a phone
number, URL, or address, and never open a link that acts (pays, signs,
unsubscribes, confirms) to find one. When nothing turns it up, say it is
missing rather than leaving the task looking complete.

Never put a password, a full card or account number, or a government ID in
a task, and don't repeat one back in your reply. Name where it is kept
instead ("login is in 1Password under the county site").

Add only what the user said or a source supports. A step, item, or reminder
you think of yourself ("bring ID") is not part of the task; if it seems worth
raising, it can be the one question you ask (Step 5).

### Related work and source

Connect the task to what it belongs to: the project, the parent card or
issue, the meeting, or the other tasks it depends on or unblocks. Link to
the source it came from (the email thread, the message, the meeting notes,
the ticket) and, when it helps, say in a few words how it came up ("Sam asked
in Tuesday's planning meeting"). A task from a meeting always names the
meeting's title, date, and time, and, when they help, the topic and why the
item exists. A task that has lost its source has lost
the thing that explains it. Follow the user's own rules about which way
links may point; some trackers are private, and links go from them, not to
them.

## Step 5: Present it

The content from Steps 1 to 4 is the skill; the format is only its
container. The same task can be written as a labeled block, a sentence or
two of prose, a rich text or Markdown checklist, an outline, or an email
whose subject is the title and whose body holds the details. Whatever the
form, it carries the same content: the verb-first title in the most
prominent spot (a heading, the first line, the checklist item, the subject),
then the outcome, contexts, dates, resources, and links. A format never
licenses dropping a detail, and a detail never forces a format.

Choose the format in this order:

1. **The one the user asks for** ("as an email to myself", "as a
   checklist", "in a sentence").
2. **The one the destination needs.** A tracker's fields (Step 6), a
   Markdown file's existing style, a notes app's checklist, an email's
   subject and body. When another skill sets the reply's shape (triage's
   item reply, or meeting notes' action items section), use that shape and
   this content.
3. **Otherwise, the labeled block below**, leaving out any line with nothing
   to say:

```
Title:     Renew the car registration online
Notes:     Done when the confirmation email arrives. Fee is $86, card on file.
           Portal: https://dmv.example.gov/renew  (from the DMV notice, Oct 30)
Contexts:  @computer
Due:       Nov 14 (the expiry on the notice)
Links:     https://mail.example.com/thread/18c2f (the DMV notice email)
```

The same task as an email to oneself:

```
Subject: Renew the car registration online

Due Nov 14, the expiry on the DMV notice (Oct 30). Do it at a computer:
https://dmv.example.gov/renew. The fee is $86, card on file. Done when the
confirmation email arrives.

Notice: https://mail.example.com/thread/18c2f
```

A compact list, such as a meeting's action items, gives each task one line:
the owner, the verb-first action, and the date in the meeting's words with
its calendar date. The rest of the content (the source meeting, resources,
contexts) goes in the filed task's description, and the line links to the
task once it exists:

```
- [ ] Lena Fischer: Publish the Q4 on-call schedule by Friday (Aug 28, 2026)
- [ ] [Jordan Lee: Send the vendor shortlist to finance by Sep 10, 2026](https://tracker.example.com/T-482)
```

Links hold actual links: URLs, or item keys the tracker can resolve. A
source you only know by name ("the DMV notice") is named as where a detail
came from, not presented as a link.

Then, in one short message, note anything you could not find (a missing
phone number, a date to confirm) and ask at most one question. When the
missing piece is a hard deadline or a check-in date, that is the question.

Write it in the user's language and voice. Use full names for people when
you can resolve them, and leave a name as given when you can't rather than
guess. For several tasks from one request, present them together, one per
block, item, or section in whatever format was chosen.

## Step 6: Offer to file it

Offer to add the task to the user's tracker, and file it only on a yes, or
when the user asked you to add it up front ("add a card for this"). When a
skill that calls this one says whether to offer (meeting notes create tasks
only when the user asks), follow it.

- **Where:** the tool the user named, or the one the conversation makes
  clear. When several are connected and nothing says which, ask. Ask for the
  board, project, or list when it isn't clear, and follow the user's
  preferences or an existing pattern for position (top or bottom) when there
  is one.
- **Check for a duplicate first.** Search the target for an item that
  already covers the action. If one exists, propose updating it instead of
  creating a second.
- **Map the fields to the tool.** The title goes to the title field, notes to
  the description, contexts to the tool's labels, tags, location, or list, the
  due date to the due field, and links to links or attachments when the tool
  has them. Use only the labels, tags, and lists the target already has.
  Leave an assignee empty on a personal board where the user is the only
  member.
- **After filing,** reply with a link to the new item and what was set. Never
  say a field was set, or a link added, unless you set or added it.
- **When filing fails,** say so with the error, leave that task unfiled, and
  ask how to proceed. Never skip one silently, and never create a test or
  placeholder item to see whether the tool works.

When no tracker is connected, the presented task is the deliverable: give it
in the format Step 5 chose, ready to paste.
