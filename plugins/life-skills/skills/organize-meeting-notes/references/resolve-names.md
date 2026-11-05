# Resolving Names of People Mentioned

Read this in Step 4 for every person named in the notes, the transcript, or
chat: attendees, and people who are only mentioned in the discussion. A bare
first name or a garbled one is a gap to research, not a question to ask
straight away.

Two kinds of name keep the ask-only rule and are not covered here: a
generic transcript speaker label (`Speaker 2`), identified as the Step 5
quote rule says, and an action item's owner, found as Step 7 says. Never
propose a name for either.

## Sources, in Order

Work through these until one settles the name, using whichever the session
can reach. The same research runs in any environment: a reporting line may
come from a chat profile, an Atlassian people lookup, or the relationships
in a contacts app.

1. **Event records from the meeting window**: the chat already read, any
   incident or project channel the discussion refers to, and the tracker
   items and pages Step 1b found. A record that shows who joined, posted, or
   did the thing described ties a person to the event.
2. **Names the user already confirmed**, in this run or in their other notes.
3. **Documents and records on the same subject, from any date**: search the
   user's earlier meeting notes (the working folder, a notes app, a
   journal), the wiki (in Confluence, `text ~ "<first name>"` with the
   project or team the line names), the tracker (in Jira, `text ~` on the
   project, then the assignees and reporters of what it returns), and
   chat messages on that subject. A page, ticket, or earlier note that
   names the person in full in the same role (the owner of the work, the
   lead of the team) ties them to the subject.
4. **A directory search on the first name**: the user's contacts, the chat
   directory, or a people directory. Compare each match's title, team,
   department, or organization with what was said about the person.
5. **The org chart**: the reporting lines of the speaker and of anyone the
   discussion ties the person to (their manager, their manager's manager,
   their reports, their peers).
6. **Sound-alike spellings** for a garbled name (`Kathrin` for `Catrin`,
   `Shawn` for `Sean`), checked only against the people steps 1 to 5 found,
   never against the whole directory.

A short form that matches an attendee (`Ben` for an attendee named
Benjamin) is not that attendee when the line speaks of the person as
someone else, such as someone the attendees are waiting on or cannot get
time with. Research the name as any other.

## Tiers

Sort each result into one tier and act on it:

- **Confirmed**: a record ties the person to the event or its subject
  (they posted in the incident channel, they created the item, a page or
  ticket names them as the owner of the work discussed, the user named
  them). Use the full name, and report the source.
- **Likely**: exactly one directory match whose title, organization, or
  reporting line fits what was said, and no other match fits. Use the full
  name without asking, and list it in the report with its evidence, so the
  user can overrule it.
- **Possible**: several plausible matches, a weak fit, or a sound-alike
  candidate. Write `First (Last?)` in the notes, using the candidate's
  first name for a garbled one, and ask, naming the candidate and the
  evidence.
- **No match**: ask, and say what was searched.

A match is likely only when its fit is specific. Sharing a first name with
the only person in a large directory is not a fit; a title that names the
team, project, or role the discussion mentioned is.

For example, the note `omar's data platform team owns the export job`,
with a directory search for Omar returning a Director, Data Platform and an
Account Executive, is likely: only one title fits. A garbled `kathrin`,
with no directory match but a Catrin Hale who is the speaker's manager, is
possible: the reporting line makes Catrin Hale a candidate, not a match.

## Asking

Ask about possible and no-match names as Step 4 asks any question,
restating the meeting, where the name came up, the quote, what was
searched, and the candidate with its evidence. For example: `In the Design
Review, Noor said "kathrin signed off on the color tokens". No one named
Kathrin is in the chat directory or your contacts; Catrin Hale, Noor's
manager, sounds similar. Is that who Noor meant?`

## Reporting

List every researched name under Step 8's "Resolved from sources" with its
tier and evidence, for example `Omar: Omar Haddad, likely (title Director,
Data Platform fits the data platform team; Omar Reyes, Account Executive,
does not)`. A name still unknown after asking goes under "Still
unknown" with what was searched.
