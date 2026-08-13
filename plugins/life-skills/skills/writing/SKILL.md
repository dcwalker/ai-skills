---
name: writing
description: >
  Compose prose in the user's own voice by researching what they have already
  written in the same medium to the same kind of audience, then drafting from
  an evidence-backed style profile. Use whenever the user wants help writing or
  rewriting a Slack message, email, text message, journal entry, blog post,
  meeting notes, status update, comment, or any other prose artifact. Also
  triggers for: "write a message to", "draft an email", "help me reply",
  "write a post", "journal about", "take notes on", "make this sound like me",
  "does this sound like me", "rewrite this in my voice". Applies to short and
  throwaway requests too ("just write it", "quick note to", "don't overthink
  it"), where the research is skipped but the voice still matters.
metadata:
  category: life-skills
---

# Writing

Write prose that sounds like the user wrote it, not like an assistant wrote it
for them. The method is research first, draft second: find real samples the
user authored in the same medium, for the same audience or an equivalent one,
derive an explicit style profile from those samples, show that profile, and
only then draft.

Voice is audience-dependent. The same person writes a two-line lowercase Slack
message to a teammate, a structured email to a client, and an unpunctuated
note to themselves. A profile is therefore always scoped to a
**(medium, audience)** pair, never to the person in general.

This skill stores no facts about any individual. Every observation it makes is
derived at runtime from samples it actually found, which is what makes it
reusable by anyone.

## When to Use

- The user asks for help writing or rewriting any prose artifact
- The user asks whether a draft sounds like them
- Another skill is about to produce user-facing prose and voice matching matters

## When Not to Use

- Code, configuration, commit messages, or PR descriptions governed by a repo
  convention. Follow the convention instead.
- The user explicitly asks for a specific external voice or a template.

## Relationship to Other Skills

- `conduct-interview` establishes **what to say** when the substance is not yet
  known. This skill establishes **how it should sound**. When the user has a
  topic but not the content, run the interview first, then apply this skill to
  the draft. When the content is already clear, skip the interview.
- `organize-meeting-notes` owns the structure of journaled meeting notes. This
  skill supplies the voice inside that structure.

---

## Step 1: Frame the Task

Establish four things before any research. Take what the request already
states, ask only about what is genuinely missing, one question at a time.

| Attribute | What to settle |
|---|---|
| **Medium** | Slack/chat, email, text/SMS, journal entry, blog post, notes, comment, document |
| **Audience** | A named person, a named group, a public readership, or the user themselves |
| **Purpose** | Inform, ask, decline, persuade, apologize, record, celebrate, vent |
| **Constraints** | Length, deadline, anything that must or must not appear |

**Audience is not optional.** If the request names a medium but no recipient
("write an email about the outage"), ask who it goes to before researching.
Researching the wrong audience produces a confident profile for the wrong
voice, which is worse than no profile.

If the user names a recipient this skill has no way to identify, ask who they
are to the user rather than guessing from the name.

---

## Step 2: Check the Cache

Research is expensive, and voice changes far more slowly than the requests
that draw on it. Cache what is found, and reuse it until there is a reason
not to.

**Location:** `${XDG_CACHE_HOME:-$HOME/.cache}/writing-style/`, created
`chmod 700` on first use. It lives in the user's home directory, not in a
shared temp path: these files hold observations derived from private
correspondence, and a world-readable location exposes them to every other
user and session on the machine. Contents:

```
identity.md                       Who the user is, in identifiers
index.md                          Searches already run and what they returned
card-<medium>-<audience-slug>.md  One style card per (medium, audience) pair
```

### identity.md

The single most useful thing in the cache. Authorship matching needs the
user's account identifiers, relationship inference needs their team and org,
and both are otherwise rediscovered from scratch every session. Written once,
edited by hand whenever something changes:

```markdown
# Identity

Name:     <full name>, and any other form that appears as a display name
Mail:     <address>, <alias>, <alias>
Chat:     <workspace>: <user id> (@<handle>)
Forge:    <github/gitlab handle>
Tracker:  <jira/linear account id>
Org:      <employer>, <primary email domain>
Team:     <team name>, <how the team is named in the directory or tracker>

## Relationships

<name or address>: <class> — <note>
```

Rules for it:

- **The user's declarations win over inference.** A relationship recorded here
  is the answer; the Step 4 signals only fill what it does not cover. If a
  directory contradicts it, say so rather than silently overriding either.
- **It is a matcher, not a claim about the world.** Use the identifiers to
  decide which samples are the user's. Do not use the file's contents as facts
  in a draft.
- **Verify before trusting a stale entry.** An identifier that matches no
  connected account is worth mentioning once; accounts get renamed.
- **Offer to write it, do not assume it.** On the first run, discover what the
  connected accounts report, show the user what would be recorded, and write
  it only if they agree. It persists, and it is theirs.
- **Identifiers only.** Never passwords, tokens, API keys, or session
  cookies. Nothing in this file should be a credential.

The cache persists across sessions and days, because voice changes slowly and
the research is the expensive part. To force a full rebuild, delete the
directory; to rebuild one profile, delete its card.

Cache rules:

- **Check identity first.** If `identity.md`'s accounts are not the ones this
  session is connected to, the cache belongs to someone else: do not read its
  cards, and start a new cache rather than mixing two people's voices.
- Read `index.md` next, and never re-run a search it records within the same
  session.
- An exact `(medium, audience)` hit is reused directly. Say so, with the date
  it was built ("reusing the Slack/teammate profile from 14 March"), rather
  than silently skipping the research step.
- A partial hit is a starting point, not an answer. Same person, different
  medium means the relationship read carries over and the mechanics do not:
  keep the audience findings, research the medium fresh.
- Corpus notes are reusable across cards. A sample found while building one
  card counts as evidence for another if it matches that card's scope.
- **Refresh on age or on drift.** A card older than about six months gets a
  quick re-check against the newest samples before it is used, and the card
  records the date of the newest sample behind it. A relationship that has
  visibly changed (a peer became a manager, a client became a friend) invalidates
  the card regardless of age.
- New samples extend a card rather than replacing it. Re-running research adds
  the messages written since, and updates the counts.
- The cache holds derived observations and short excerpts only, never bulk
  copies of correspondence.

---

## Step 3: Discover Available Sources

Survey what this session can actually reach before searching. Check which MCP
servers are connected, which skills are available, which CLIs respond to
`command -v <tool>`, and which local directories exist. Use only what is
genuinely reachable. Never imply a source was consulted when it was not.

Common sources, by what they hold:

| Source | Yields |
|---|---|
| Email (Gmail MCP or equivalent) | Sent mail: the richest and most reliably attributable corpus |
| Team chat (Slack MCP or export) | Short-form professional voice, per-channel and per-DM |
| Local files (`~/journal`, notes dirs, repo Markdown, Obsidian vaults) | Journal entries, notes, drafts, long-form |
| Google Drive / Docs | Long-form documents, meeting notes, published drafts |
| Issue trackers (Jira, Trello, GitHub) | Comments, descriptions, status updates |
| Wikis (Confluence, Notion, GitHub wikis and Pages, repo docs) | Explanatory long-form written for colleagues, usually the most structured register |
| A personal site or blog | Public long-form at the highest polish tier |

Wikis are worth reaching for early. They hold the register between a ticket
comment and a published post, they are attributable through page history, and
most people have more of this writing than they have blog posts.

A personal site is the one source to approach carefully. Do not search the
open web for the user's name and treat what comes back as theirs: names are
shared, and a misattributed site poisons every observation drawn from it. Use
a site only when the user names it, or when an authenticated source links to
it (a profile page on a connected account, a repository the user owns). If
authorship cannot be established that way, skip it and say so.

Text and SMS rarely have a tool seam. Do not fabricate one. Fall back down the
ladder in Step 4 and say which substitution was made.

---

## Step 4: Build the Corpus

Search in this order and stop as soon as the sample target in Step 5 is met.
Record which rung supplied each sample; the style card reports it.

1. **Same medium, same audience.** Prior messages the user sent to this exact
   person or channel.
2. **Same medium, same relationship class.** Other recipients who stand in the
   same relation to the user (see the table below).
3. **Adjacent medium, same audience.** Chat and text are adjacent; chat and
   short email are adjacent; journal and personal notes are adjacent; blog and
   long-form documents are adjacent.
4. **Adjacent medium, same relationship class.**
5. **Any medium, any audience**, used only for medium-independent traits:
   recurring vocabulary, humor, hedging habits, favored connectives. Label
   these as cross-medium observations, never as evidence about format or
   polish.

Never skip a rung silently. Dropping from rung 1 to rung 3 is a finding the
user should see.

### Inferring the relationship class

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

### Authorship filter

A sample only counts if the user wrote it, and a display name is not proof
that they did. Names are shared, accounts get renamed, and one wrong
attribution contaminates every count on the card.

**Establish the user's identifiers first.** Take them from the cache's
`identity.md` when it has them, and otherwise from the connected accounts
themselves rather than from the conversation: the email addresses and aliases
the mail account actually sends from, the chat workspace's user ID, the forge
handle (GitHub, GitLab) of the authenticated account, the tracker account ID.
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

---

## Step 5: Analyze the Samples

Target 5 to 10 samples in the primary bucket. Confidence follows the count and
the rung they came from:

| Evidence | Confidence |
|---|---|
| 5+ samples at rung 1 or 2 | High |
| 3 to 4 samples, or a mix of rungs 1 to 3 | Medium |
| 1 to 2 samples, or rung 4 to 5 only | Low |
| None | See Step 6's no-evidence path |

Extract only what the samples actually show. Every claim on the style card must
be traceable to a count ("first name only, 7 of 9 samples"), not to an
impression.

**Structure:** typical length in words or lines, paragraph count and size,
whether the ask comes first or last, use of bullets versus prose, headers,
whether context precedes or follows the point.

**Openers and closers:** greeting form or absence, sign-off form or absence,
name form used for the recipient, self-reference.

**Sentences:** median length, variance, fragments, questions, imperatives,
starting words and connectives.

**Vocabulary:** recurring words and phrases, domain jargon and abbreviations,
intensifiers, hedges, profanity, filler, words conspicuously absent.

**Tone:** directness, warmth markers, humor and its type, apology and gratitude
habits, how disagreement and bad news get delivered.

**Mechanics:** capitalization, punctuation habits (em dashes, semicolons,
ellipses, exclamation marks), contractions, Oxford comma, formatting,
deliberate typos or shorthand.

**Emoji and reactions:** which ones recur, where they sit (inline, trailing, as
a reaction instead of a reply), and how dense they are per message. Note the
audiences that get none, since that boundary is usually sharp and a stray
emoji in the wrong register is one of the loudest tells there is.

**Platform conventions.** These are learned habits rather than prose style,
and getting them wrong reads as "someone else's account" faster than a wrong
adjective does. Count them the same way:

- **People:** an `@mention` versus a written-out name, first name versus full
  name, and whether the mention is used for addressing, for crediting, or for
  pulling someone into a thread.
- **Links:** a bare URL, a hyperlink on descriptive text, or a reference-style
  link. Whether the link is explained before it is dropped, and whether the
  channel's own unfurl is left to do the work.
- **Images:** how often a screenshot stands in for a description, whether it
  is annotated, and whether a caption accompanies it or the image goes bare.
- **Threading and formatting:** replying in-thread versus posting anew, code
  blocks versus inline backticks, quoting versus paraphrasing, and structural
  conventions the platform affords that the user does or does not take up.

**Polish tier**, on this ladder:

| Tier | Markers |
|---|---|
| **1 — Fire-off** | One or two lines, no greeting or sign-off, lowercase, fragments, abbreviations, typos left alone |
| **2 — Quick note** | First-name greeting or none, contractions, one to three short paragraphs, minimal formatting, one clear ask |
| **3 — Considered** | Greeting and sign-off, complete sentences, deliberate structure, explicit ask and context, proofread |
| **4 — Formal / public** | Full structure, careful diction, no slang, edited for a reader who may quote it |

The tier comes from the samples, not from the topic's importance. Where the
current situation differs from every sample (bad news to someone the user only
ever jokes with, a first message to a new client), say so and confirm the tier
before drafting.

---

## Step 6: Present the Style Card

Show the card and get a response before drafting. This is the reference the
draft is written against, and the point at which the user can correct a wrong
read cheaply.

```
Style Card: <medium> to <audience> (<relationship class>)

Evidence:    <N> samples | <sources> | <date range> | rung <n>: <what matched>
             matched on <identifier used to confirm authorship>
Confidence:  high | medium | low
Polish:      Tier <n> — <name> (<one line of evidence>)

Opening:     <observed pattern, with counts>
Structure:   <length, ordering, formatting>
Sentences:   <length, rhythm, fragments>
Vocabulary:  <recurring words, jargon, absences>
Tone:        <directness, warmth, humor, how hard things get said>
Mechanics:   <capitalization, punctuation, contractions>
Emoji:       <which, where, how dense, and to whom none are sent>
Conventions: <mentions vs written names, links, screenshots, threading>
Closing:     <observed pattern, with counts>
Avoid:       <specific tells absent from every sample>

Gaps:        <what the samples do not cover for this request>
Built:       <date> | newest sample <date> | reused from cache | rebuilt
```

Ask: "Does this match how you'd write it? Anything to adjust before I draft?"

### When there is no usable evidence

Say so plainly. Do not fill the gap with a generic professional voice and do
not present an unevidenced card as if it were researched. Instead:

1. Report which sources were searched and what came back empty.
2. Ask the user to paste one or two examples of their own writing in this
   medium, which is the fastest path to a real profile.
3. If they decline or have none, offer a short calibration: polish tier from
   the Step 5 ladder, greeting and sign-off preference, and target length. Draft
   from that, and label the card `Confidence: none, user-declared`.

If the user asks to skip the research entirely ("just write it", "don't go
digging"), honor it. Two things still hold: say once, in a single line, that
the draft is unresearched so they read it with that in mind, and add no facts
they did not give you. A skipped research step lowers the confidence of the
voice, never the standard for the content.

---

## Step 7: Draft

Write to the card. Then check the draft against it line by line, because
assistant defaults reassert themselves during drafting.

Remove these unless a sample actually shows them:

- Warm-up boilerplate: "I hope this finds you well", "I wanted to reach out",
  "Just checking in", "Thanks for your patience"
- A closing offer of further help
- Rule-of-three lists and balanced parallel clauses
- Em dashes, semicolons, and ellipses the user does not use
- Bullets where the user writes prose, or prose where the user writes bullets
- Uniform sentence length, and every paragraph the same size
- Hedging stacks: "it might be worth considering whether we could perhaps"
- Restating the recipient's own message back to them
- A greeting or sign-off the samples do not have
- Emoji at a density the samples do not support
- Corrected capitalization, expanded abbreviations, or repaired shorthand where
  the user's own habit is otherwise
- Vocabulary that appears nowhere in the corpus, especially escalations like
  "leverage", "utilize", "align", "delve", "robust"

Match the observed length. If the samples run 40 words, a 200-word draft is
wrong even if every sentence is in voice.

**Copy style from the samples. Never copy facts from them.** The corpus is
evidence about how the user writes, not about what is true today. A running
joke, a recurring to-do, a project thread, a person who appears in every
sample: reproducing any of those puts a claim in the artifact that the user
did not make. This is the failure mode that voice matching invites, because
continuity feels like fidelity. It is fabrication.

Never fabricate facts to fill the draft, from the corpus or from anywhere
else. If something needed is unknown, mark it (`[confirm date]`, `[name TBD]`)
and say so, rather than inventing it. Filling a section because the samples
always have one is not a reason: write the shorter artifact.

Do not sharpen what the user left vague. "Tomorrow" does not become "tomorrow
morning", "next week" does not become "Tuesday", "a few" does not become
"three", and "the migration" does not acquire a cause. Added precision reads
as harmless because it is small and plausible, and it is still invention: the
user has to notice and undo it before sending.

Instructions about the conversation are not content for the artifact. "I will
not be around to answer", "keep it short", "make it sound friendlier" shape how
you work; they are not facts about the user to be written into the message.

Present the draft, then a short note of any place the request forced a
departure from the card.

---

## Step 8: Revise and Feed Back

- Make requested changes precisely. Do not rewrite approved sentences.
- Every correction is evidence. When the user changes a word, a greeting, or a
  length, update the cached card so the next artifact in the session inherits
  the fix.
- If a correction contradicts the samples, keep the user's version and note the
  conflict on the card. The user outranks the corpus.
- If the user asks for another artifact, return to Step 2. The cache makes the
  second one fast.

---

## Delivery and Privacy Rules

- Research is read-only. Never send, post, or reply while gathering samples.
- Never send or post the deliverable. Save a draft only after the user confirms
  the text, and tell them where it landed.
- Keep excerpts on the style card short, only long enough to evidence a claim.
- Do not carry content from someone else's message into the deliverable, and do
  not quote a third party's writing as the user's own style.
- Corpus material stays in the cache and out of the deliverable, the
  repository, and any commit. The cache is the user's own directory, holds
  derived observations rather than copies of correspondence, and is theirs to
  delete: say where it lives the first time this skill writes to it.

---

## Quality Rules

- Research before drafting. A draft that appears before a style card has skipped
  the only step that makes it sound like the user.
- Every claim on the card traces to samples that were actually read. No claim is
  stated more confidently than its evidence supports.
- Scope every profile to a (medium, audience) pair. Never reuse a profile across
  audiences without saying so.
- Report the rung the evidence came from, and report empty searches rather than
  hiding them.
- Ask for the audience when it is missing. Never infer it from the topic.
- Never invent facts, names, dates, or events to fill a draft, and never
  import them from the samples. Style is copied; content never is.
- Keep the cache in the user's own home directory, and confirm its recorded
  identity matches the current accounts before reading it.
- Confirm authorship by account identifier, never by display name alone.
- Match observed length, punctuation, and polish, including habits that look
  like errors.
- Update the cache with every correction the user makes.
- The user's stated preference always outranks the corpus.
