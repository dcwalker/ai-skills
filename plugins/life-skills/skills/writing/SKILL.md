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
  "does this sound like me", "rewrite this in my voice".
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

## Step 2: Check the Session Cache

Research is expensive and the same session often produces several artifacts.
Cache what is found.

**Location:** use the agent's session scratch directory if it has one,
otherwise `${TMPDIR:-/tmp}/writing-style/`. Contents:

```
index.md                          Searches already run and what they returned
card-<medium>-<audience-slug>.md  One style card per (medium, audience) pair
```

Cache rules:

- On every run, read `index.md` first. Never re-run a search it records.
- An exact `(medium, audience)` hit is reused directly. Say so ("reusing the
  Slack/teammate profile built earlier in this session") rather than silently
  skipping the research step.
- A partial hit is a starting point, not an answer. Same person, different
  medium means the relationship read carries over and the mechanics do not:
  keep the audience findings, research the medium fresh.
- Corpus notes are reusable across cards. A sample found while building one
  card counts as evidence for another if it matches that card's scope.
- A card written on an earlier date may be reused, but say when it was built
  and offer to refresh it.
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
| A personal site or blog (WebFetch) | Public long-form at the highest polish tier |

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
evidence, not from the name. Useful signals: the address book entry and its
groups, the email domain (shared employer, client, vendor, personal provider),
shared calendar events and their size and recurrence, reporting hints in a
directory or ticket tracker, message frequency and time of day, and how the
recipient addresses the user.

| Class | Typical signals |
|---|---|
| Close personal | Personal email domain or phone, family or friend group in contacts, off-hours contact, informal salutations |
| Peer / teammate | Same employer domain, recurring team meetings, shared channels and tickets |
| Manager / leadership | Same domain, one-on-one recurring meeting, escalation or approval language |
| Direct report | Same domain, one-on-one recurring meeting, delegation or feedback language |
| External professional | Different domain, scheduled calls, contract or account context |
| Cold / unknown | No prior contact anywhere |
| Public / broadcast | No single recipient: a blog, an announcement, a channel post to a wide audience |

State the inferred class and the signals behind it. If the signals conflict, or
none are found, ask rather than guessing.

### Authorship filter

A sample only counts if the user wrote it.

- Email: search sent mail (`in:sent`, `from:me`). Strip quoted reply chains,
  forwarded bodies, and signature blocks before analyzing.
- Chat: only the user's own messages. Exclude pasted links, quoted text, and
  bot or automation output.
- Documents: only content the user authored. If a document is collaborative and
  authorship per section cannot be established, skip it.
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
ellipses, exclamation marks), contractions, Oxford comma, emoji and reaction
use and density, links, formatting, deliberate typos or shorthand.

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
Confidence:  high | medium | low
Polish:      Tier <n> — <name> (<one line of evidence>)

Opening:     <observed pattern, with counts>
Structure:   <length, ordering, formatting>
Sentences:   <length, rhythm, fragments>
Vocabulary:  <recurring words, jargon, absences>
Tone:        <directness, warmth, humor, how hard things get said>
Mechanics:   <capitalization, punctuation, contractions, emoji>
Closing:     <observed pattern, with counts>
Avoid:       <specific tells absent from every sample>

Gaps:        <what the samples do not cover for this request>
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

If the user asks to skip the research entirely, do it, and say once that the
draft is unresearched so they read it with that in mind.

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

Never fabricate facts to fill the draft. If something needed is unknown, mark
it (`[confirm date]`, `[name TBD]`) and say so, rather than inventing it.

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
- Corpus material stays in the session cache and out of the deliverable, the
  repository, and any commit.

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
- Never invent facts, names, dates, or events to fill a draft.
- Match observed length, punctuation, and polish, including habits that look
  like errors.
- Update the cache with every correction the user makes.
- The user's stated preference always outranks the corpus.
