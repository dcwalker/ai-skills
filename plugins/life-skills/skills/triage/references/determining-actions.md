# Determining Actions

Step 6 in full: how to name an item's next action as something the user does,
what to do when the next move belongs to someone else, and where a time or
place gets recorded. Read this whenever the action is not obvious from the
item alone.

## The action is the user's, in one of three kinds

What counts as an action, and how to phrase each of the three kinds (now, at
a time or place, and a check-in on someone else's move), is create-task's
Step 1. Triage applies it to each item and adds only this:

- An item with no action is reference (keep it, file it), someday (park it),
  or noise (delete or archive it). Say which in the item's reply.
- A "now" action under two minutes is offered under the 2-minute rule and
  done in this run only on a yes. Longer, it is captured as an action.
  Either way, triage does not start the task on its own (SKILL.md Step 6).
- A place goes in the title when it is where the action happens, or in a
  context label when the scope uses them; a time becomes a due date or a
  calendar entry the way the scope records it (below).

## Linked content first

Step 5a follows the item's links before this step for a reason: the ask often
lives behind them. A card titled "follow up" whose link opens a thread asking
the user to deliver something by Friday has the action "Deliver it by Friday",
not "Follow up". When the item's own text and its linked content disagree,
the linked content wins, and the proposal says so ("the linked thread asks for
X, so the title now says X"). A link that could not be opened is reported as
unresolved; the action is not guessed from its URL.

## When the action needs a date

Never invent a date. A date comes from the item, its links, or the user:

- A date written in the item or a linked page ("by Friday, Oct 9", "the quote
  is valid until the end of August") is the date. A relative date resolves
  against the date of the message or comment that says it.
- A promise someone else made ("I'll send it by Thursday") sets a check-in's
  date: the day the promise falls due.
- With no date anywhere, ask for a check-in or a fixed appointment; any
  other action is left without a date (SKILL.md Step 7, "Due Date"). "Next
  week" or "in a few days" picked by you is an invented date.

## Finding the scope's pattern

Where a time, a place, or a check-in is recorded is the user's system, not the
skill's choice. Look at the other items in the scope for an established
pattern before proposing where this one goes:

- **Due dates.** Do similar items, especially other check-ins, carry due
  dates? Then this one gets a due date too, when the item, its sources, or the
  user gives the date. The pattern decides where a date goes, never that one exists.
- **A waiting-for list or label.** Is there a waiting-for list on the board,
  or a waiting-for label in use? Check-ins go there.
- **The preferences file.** Does it say how check-ins and due dates are
  recorded? Then that settles it.
- **Context labels.** Do items carry place or context labels (`@errands`,
  `@home`, `@office`)? A place-bound action gets the matching one.
- **Titles.** Do existing check-ins share a phrasing ("Check in with X about
  Y")? Match it.
- **Calendar.** Do items reference calendar events for timed actions? Then a
  timed action is proposed as an event, never created unconfirmed.

Follow the pattern you find and name it in the proposal ("matching your other
check-ins, which carry a due date on the waiting-for list"). When the scope
shows no pattern, ask when first, then, in the item's next reply, how to
record it, offering the options that fit the platform:

> "This is a check-in with the plumber about the estimate. When should you
> check in?"
>
> "Should check-ins like this get a due date on the card, or a calendar
> reminder?"

## Presenting the action

The item's reply (Step 9) states the action on its summary line, so the user
can check it before hearing the changes it drove:

```
[Dishwasher](https://trello.com/c/abc123)
The landlord is fixing it; your action is to check in about the repair on Oct 12.
Dates:     Oct 12 (the date the landlord gave)
Labels:    Waiting
Proposed:  title "Check in with the landlord about the dishwasher repair"; due Oct 12
Retitle it and set the due date?
```
