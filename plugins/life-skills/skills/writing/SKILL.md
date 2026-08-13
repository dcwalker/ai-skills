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

**Audience decides the register, so ask when it is unknown.** If the request
names a medium but no recipient ("write an email about the outage"), ask who
it goes to. Some media answer this themselves and need no question: a journal
entry is to the user, a blog post is to a public readership.

Never invent a recipient. Researching the wrong audience produces a confident
profile for the wrong voice, which is worse than no profile at all.

**A general profile lets the question be deferred, not skipped.** When
`general.md` exists (see Step 2) and the user would rather have a draft than
answer a question, write from it and say plainly what you did: this is the
user's voice with the register left neutral, because greeting, sign-off,
formality, length, and emoji are precisely what `general.md` excludes and
precisely what changes with audience. Name the assumption, keep it correctable
in one line, and offer to tighten it once the audience is known. What is not
allowed is quietly choosing an audience and presenting the result as matched.

If the user names a recipient this skill has no way to identify, ask who they
are to the user rather than guessing from the name.

---

## Step 2: Check the Cache

Research is expensive, and voice changes far more slowly than the requests
that draw on it. Cache what is found, and reuse it until there is a reason
not to.

**Location.** Not every environment has a disk that survives the session, so
there are two cases:

1. **A persistent local filesystem:** `$HOME/writing-style/`, created
   `chmod 700` on first use. In plain sight rather than buried in a cache
   path, because it is meant to be read and edited by hand. Deliberately not
   a shared temp path: these files hold observations derived from private
   correspondence, and a world-readable location exposes them to every other
   user and session on the machine.
2. **The conversation itself**, when nothing persists: keep the profile in the
   session, and at the end offer it as a block the user can paste somewhere
   durable, such as a project's instructions or knowledge files, so the next
   session starts from it rather than from nothing.

An ephemeral container is case 2: writing to `$HOME` there is not wrong, but
it is gone when the container is, so say so rather than implying the research
was saved. Never copy the profile to cloud storage or any other location
outside the machine.

Contents:

```
identity.md                       Who the user is, in identifiers
general.md                        What holds true across every card
index.md                          Searches already run and what they returned
card-<medium>-<audience-slug>.md  One style card per (medium, audience) pair
```

All four formats are in
[references/cache-files.md](references/cache-files.md). Read it before writing
any of these files, and before relying on what one of them says. In short:
`identity.md` records the account identifiers that decide which samples are
the user's, plus their org, team, and known relationships; `general.md`
records only the traits that survive every audience, which is what a request
with no card of its own falls back to; `index.md` is the ledger of searches
already run, including the ones that came back empty.

The one format detail the rules below depend on: a stored card carries a
`Built:` line recording when it was written and how recent its newest sample
is, and **age is measured from the newest sample, not the build date** -- a
card rebuilt yesterday from samples that all predate last spring describes
how the user wrote a year ago.

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
- **Confirm a hit cheaply, do not rebuild it.** A card inside its refresh
  window earns at most one search for samples newer than its newest sample.
  If that turns up nothing, use the card as it stands. If it turns up a few,
  fold them in and update the counts. Re-reading the whole corpus a card was
  built from defeats the point of having cached it.
- A partial hit is a starting point, not an answer. Same person, different
  medium means the relationship read carries over and the mechanics do not:
  keep the audience findings, research the medium fresh.
- Corpus notes are reusable across cards. A sample found while building one
  card counts as evidence for another if it matches that card's scope.
- **Refresh on age or on drift.** When the card's newest sample is more than
  about six months old, re-check against current samples before using it, and
  say that the reading was refreshed. A card with no `Built:` line has no
  age and gets rebuilt rather than trusted.
- **Drift invalidates a card regardless of age.** When the relationship
  recorded on the card contradicts what `identity.md` or a directory now says
  (the card reads peer, the user has since recorded them as a manager), the
  register the card describes is the wrong one. Rebuild it, and say why the
  cached one was not used rather than silently swapping it out.
- New samples extend a card rather than replacing it. Re-running research adds
  the messages written since, and updates the counts.
- The cache holds derived observations and short excerpts only, never bulk
  copies of correspondence.

---

## Step 3: Discover Available Sources

Survey what this session can actually reach before searching. Check which MCP
servers are connected, which skills are available, and which CLIs respond to
`command -v <tool>`. Use only what is genuinely reachable. Never imply a
source was consulted when it was not.

**Look in the working directory first, then the home directory.** List them.
A corpus that is present at all is almost always sitting in one of those two
places, under an obvious name: `journal/`, `notes/`, `blog/`, `posts/`,
`slack-export/`, an Obsidian vault, a docs tree. Reaching for a broad
filesystem search before looking where the session is already standing is how
a corpus in plain sight gets missed, and a depth-capped `find /` will not
reach a working directory that is nested more than a few levels deep.

The sources worth checking, what each one is good for, and the two that
need care (a personal site, which is easy to misattribute, and chat, which
is the highest-volume medium and the most often unreachable) are in
[references/finding-samples.md](references/finding-samples.md), along with
how to establish a recipient's relationship class. Read it before building a
corpus for an audience with no cached card.

Text and SMS rarely have a tool seam. Do not fabricate one. Fall back down the
ladder in Step 4 and say which substitution was made.

---

## Step 4: Build the Corpus

Search in this order and stop as soon as the sample target in Step 5 is met.
Record which rung supplied each sample; the style card reports it.

1. **Same medium, same audience.** Prior messages the user sent to this exact
   person or channel.
2. **Same medium, same relationship class.** Other recipients who stand in the
   same relation to the user.
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

**Two checks before the corpus counts as gathered.** Both cost one extra call
and both are easy to skip, because in each case a plausible corpus is already
in hand and the extra work looks redundant. It is not: skipping either one
silently narrows or contaminates the evidence.

1. **Re-run the search for every retired identifier.** Open `identity.md` and
   look for `Former:` lines. For each one, issue the same search again under
   that address, handle, or account id, and add what comes back. A search
   under the current identifier alone returns only what the user wrote since
   the change, which on a recent change can be a fraction of what exists. If
   there are no `Former:` lines, say so and move on; that is a two-second
   check, not a research step.
2. **Run blame before treating any document as a sample.** A file or page with
   more than one author is not one corpus. `git blame`, `git log --author`, or
   the page history says which passages are the user's; use only those. A
   collaborative document read as though one person wrote it yields a card
   averaged across several voices, none of which is the user's, and the
   average always reads plausible.

Rungs 2 and 4 need a relationship class for the recipient, and every rung
needs samples the user actually wrote. Both are in
[references/finding-samples.md](references/finding-samples.md): infer the
class from a directory service and the user's own declarations before
guessing from message patterns, and match authorship on account
identifiers rather than display names, which collide.

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

This holds whatever shape the deliverable takes. When the artifact is an edit
to a file rather than a message to send, the edit is the draft: the card comes
first, and writing straight into the file skips the only checkpoint the user
has.

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
"three", "the first of next month" does not become a calendar date, and "the
migration" does not acquire a cause. Resolving a relative date is the most
tempting of these, because a specific date genuinely reads better. It is still
the user's date to choose. Added precision reads
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
  length, update the cached card so the next artifact inherits the fix.
- When a card is written or changed, rebuild `general.md` from the current set
  of cards, keeping only what still holds across at least three of them and
  two different relationship classes.
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
- Keep the cache where the environment can actually persist it, and confirm
  its recorded identity matches the current accounts before reading it.
- With no samples, ask the user to describe the style in their own words and
  fall back to `general.md`, labeled as cross-medium. Never dress up an
  unevidenced profile as a researched one.
- Confirm authorship by account identifier, never by display name alone.
- Match observed length, punctuation, and polish, including habits that look
  like errors.
- Update the cache with every correction the user makes.
- The user's stated preference always outranks the corpus.
