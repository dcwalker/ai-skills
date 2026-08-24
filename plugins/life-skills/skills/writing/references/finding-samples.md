# Finding samples

Reference for the `writing` skill, Steps 3 and 4: which sources hold which
kind of writing, how to work out what a recipient is to the user, and how to
be sure a sample was written by the user at all. Read it when building a
corpus for an audience with no cached card.

## Where the writing lives

Common sources, by what they hold:

| Source | Yields |
|---|---|
| Email (Gmail MCP or equivalent) | Sent mail: the richest and most reliably attributable corpus |
| Team chat (a chat MCP, or a workspace export on disk) | Short-form professional voice, per-channel and per-DM |
| Local files (`~/journal`, notes dirs, repo Markdown, Obsidian vaults) | Journal entries, notes, drafts, long-form |
| Google Drive / Docs | Long-form documents, meeting notes, published drafts |
| Issue trackers (Jira, Trello, GitHub) | Comments, descriptions, status updates |
| Wikis (Confluence, Notion, GitHub wikis and Pages, repo docs) | Explanatory long-form written for colleagues, usually the most structured register |
| Git history and the code host (`git log --author`, prior PR descriptions) | Commit bodies and PR narrative: terse, technical, written for whoever reads it later |
| A personal site or blog | Public long-form, usually the most edited writing a person has |

Wikis are worth reaching for early. They hold the register between a ticket
comment and a published post, they are attributable through page history, and
most people have more of this writing than they have blog posts.

Chat is the highest-volume medium most people have, and the one most often
unreachable. When no chat tool is connected, look for a workspace export on
disk before giving up: an export is a directory of per-channel, per-day JSON
with the author recorded as a user id, which is better evidence than the API
would give and needs no connector. Match on that id, and keep channel samples
separate from direct-message samples, because the same person writes those two
places differently.

Do not assume a tier for any of these. A blog is edited, but plenty of people
write theirs in fragments and lowercase; the tier comes from the samples, as
Step 5 says, not from what the medium sounds like it should be.

A personal site is the one source to approach carefully. Do not search the
open web for the user's name and treat what comes back as theirs: names are
shared, and a misattributed site poisons every observation drawn from it. Use
a site only when the user names it, or when an authenticated source links to
it (a profile page on a connected account, a repository the user owns). If
authorship cannot be established that way, skip it and say so.

## Inferring the relationship class

When there are no samples for a named recipient, infer the relationship from
evidence, not from the name.

**Start from what the user has already told you.** A relationship recorded in
`identity.md` is settled; so is the team named there, which turns "is this
person a teammate" into a membership check rather than a guess.

**Then check a directory service when one is reachable.** A workspace
directory, an org chart, or an HR or identity system states the reporting line
and team membership as fact, where channel membership and meeting patterns only
hint at them. People sit in channels they do not work in and skip meetings they
do belong to; a directory entry says who reports to whom. Use the inferred
signals below to fill what the directory does not cover, or when there is no
directory at all.

Secondary signals: the address book entry and its groups, the email domain
(shared employer, client, vendor, personal provider), shared calendar events
and their size and recurrence, message frequency and time of day, and how the
recipient addresses the user.

| Class | Typical signals |
|---|---|
| Close personal | Personal email domain or phone, family or friend group in contacts, off-hours contact, informal salutations |
| Peer / teammate | Same team in the directory; failing that, same employer domain, recurring team meetings, shared channels and tickets |
| Manager / leadership | The directory's reporting line; failing that, a recurring one-on-one plus escalation or approval language |
| Direct report | The directory's reporting line, read the other way; failing that, a recurring one-on-one plus delegation or feedback language |
| External professional | Different domain, scheduled calls, contract or account context |
| Cold / unknown | No prior contact anywhere |
| Public / broadcast | No single recipient: a blog, an announcement, a channel post to a wide audience |

State the inferred class and the signals behind it. If the signals conflict, or
none are found, ask rather than guessing.

**A channel is not a person and does not take a relationship class.** Scope a
channel card to the channel itself, by name and id. What sets its register is
not a relation to the user but three properties of the room, and they belong on
the card, because they are what a later session needs in order to judge whether
some other channel is a fair substitute:

| Property | Why it moves the register |
|---|---|
| Membership | A six-person team channel and a two-hundred-person announcement channel are different rooms, whoever is writing |
| Purpose | Discussion, incident response, standup, announcements, and social each carry their own conventions |
| Subject | A channel about one system accumulates shorthand that reads as noise anywhere else |

Rung 2 for a channel therefore means another channel matching on those three,
not merely another channel in the same workspace. When nothing matches, name
the channel that was substituted and which of the three it differs on. Treating
any team channel as interchangeable with any other is the channel-shaped
version of averaging two people's voices together.

## Authorship filter

A sample only counts if the user wrote it, and a display name is not proof
that they did. Names are shared, accounts get renamed, and one wrong
attribution contaminates every count on the card.

**Establish the user's identifiers first.** Take them from the cache's
`identity.md` when it has them, and otherwise from the connected accounts
themselves rather than from the conversation: the email addresses and aliases
the mail account actually sends from, the chat workspace's user ID, the code
host handle (GitHub, GitLab) of the authenticated account, the tracker
account ID.
Anything discovered this way is worth writing back to `identity.md`, with the
user's agreement, so the next session starts from it.
Then match samples on those identifiers. Fall back to a name match only when
no identifier is available, and mark anything attributed that way as
provisional evidence on the card.

- Email: search sent mail (`in:sent`, `from:me`), matched on the account's own
  addresses. Strip quoted reply chains, forwarded bodies, and signature blocks
  before analyzing.
- Chat: only messages whose author ID is the user's, not whose display name
  looks right. Exclude pasted links, quoted text, and bot or automation output.
- Documents and wiki pages: attribute through revision history rather than the
  document's owner or last editor. Page history, `git blame`, and per-revision
  diffs identify which passages the user actually wrote, which is what makes a
  collaborative document usable instead of disqualifying. Skip only what the
  history cannot resolve.
- Exclude anything auto-generated: out-of-office replies, templates, calendar
  invitations, form letters, and text the user pasted from elsewhere.

Prefer samples from the last 12 to 24 months. If the only samples are older,
say so; voice drifts.

## Slugging a channel card

**A channel is an audience in its own right.** Slug it with the channel's own
name and, where the workspace exposes one, its id:
`card-slack-platform-eng-C024BE91L.md`. Never slug a card by a category such as
`private-channel` or `team-channel`. Two channels in one workspace differ in
who is in them, what they are for, and what they are about, and those are
precisely the things that set register, so a card spanning both describes
neither. A channel and a direct message with someone who is in that channel are
likewise two audiences, not one.

## When no samples exist at all

Say so plainly. Do not fill the gap with a generic professional voice and do
not present an unevidenced card as if it were researched. Instead:

1. Report which sources were searched and what came back empty.
2. **Fall back to `general.md`** if the cache has one, and label it for what
   it is: how this person writes in general, not how they write to this
   person. It covers punctuation, recurring words, and instincts about length
   and directness. It cannot tell you the greeting, the sign-off, or the
   formality, which is precisely what is missing here.
3. **Ask the user to describe how it should sound**, in their own words.
   "Blunt, no greeting, two lines" is a better instruction than any ladder of
   options, and it is faster to give than a pasted sample is to find. Prompt
   for the register and the relationship if the description leaves them open.
4. Offer the sample-paste route as an alternative rather than the first ask:
   one or two real examples turn a described style into an observed one, and
   the card built from them is reusable next time.
5. Label the result honestly: `Confidence: none, user-described` when it came
   from the description, `low, cross-medium` when it leaned on `general.md`.

Whatever the user describes is worth keeping. Write it into the card so the
next request to this audience starts from it, and mark it as user-described
rather than observed, so a later run with real samples knows it can be
replaced.

If the user asks to skip the research entirely ("just write it", "don't go
digging"), honor it. Two things still hold: say once, in a single line, that
the draft is unresearched so they read it with that in mind, and add no facts
they did not give you. A skipped research step lowers the confidence of the
voice, never the standard for the content.
