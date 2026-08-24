---
name: writing
description: >
  Compose prose in the user's own voice by researching what they have already
  written in the same medium to the same kind of audience, then drafting from
  an evidence-backed style profile. Use whenever the user wants help writing
  or rewriting any prose artifact: a Slack message, email, text message,
  journal entry, blog post, meeting notes, status update, or comment, and
  equally prose that lives in a repository -- a design doc, README, spec, RFC,
  architecture note, or a single section inside one -- and the written parts
  of a commit body or pull request description, where `commit` and `pr` own
  the required structure and this skill supplies the voice within it. A
  request that names a file path rather than a recipient still needs this
  skill: the deliverable is sentences someone will read as the user's own
  writing. Also triggers for: "write a message to", "draft an email", "help me
  reply", "write a post", "write the X section of", "add a section to",
  "journal about", "take notes on", "make this sound like me", "does this
  sound like me", "rewrite this in my voice". Applies to short and throwaway
  requests too ("just write it", "quick note to", "don't overthink it"), where
  the research is skipped but the voice still matters. Not for code or
  configuration, and not when the user asks for someone else's voice or for a
  fixed template to be filled in.
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

- Code and configuration. Their shape is set by the language, the linter, and
  the repo, and there is no prose in them to carry a voice.
- The user explicitly asks for a specific external voice or a template.

**A repository is a location, not an exemption.** The first exclusion is about
artifacts with no prose in them -- a config file, a lockfile, generated
output -- not about where a file happens to sit. A design doc, README,
spec, RFC, architecture note, or a single section inside one is prose with an
author and an audience, and it is squarely in scope even when it is
git-tracked, even when the request names a path rather than a recipient. Those
documents are also the ones most likely to have several authors, which is what
the blame rule in Step 4 exists for: reading a shared document as though one
person wrote it produces a voice belonging to nobody.

## Relationship to Other Skills

- `conduct-interview` establishes **what to say** when the substance is not yet
  known. This skill establishes **how it should sound**. When the user has a
  topic but not the content, run the interview first, then apply this skill to
  the draft. When the content is already clear, skip the interview.
- `organize-meeting-notes` owns the structure of journaled meeting notes. This
  skill supplies the voice inside that structure.
- `commit` and `pr` own the artifact and everything its convention dictates:
  what gets staged, the issue key, the conventional-commit prefix, a template's
  required sections, draft status, reviewers. This skill supplies the prose
  inside that shape -- the commit body explaining why a change was made, the
  narrative parts of a PR description. When either of them is running, follow
  its structure exactly and match voice only within it.

  **The convention outranks the corpus.** A subject line has almost no voice
  latitude: if the repo requires `fix(scope):`, it gets one whether or not a
  single sample shows it. Voice lives in the body, where someone is explaining
  a decision to whoever reads it months from now. Departing from a repo
  convention because the samples do otherwise is the one way this skill can
  leave a commit or a PR worse than it found it.

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

**Only these four attributes can hold up a draft.** Questions in this step are
about the medium, the audience, the purpose, and the stated constraints, and
about nothing else. What hours the shift runs, what the handoff involves, who
else to loop in: those are details of what the message *says*, and a request
being thin on them is the normal case, not a blocker. Draft anyway and mark
what is genuinely unknown inline -- `[confirm window]`, `[handoff details]` --
as Step 7 describes. A request naming the medium, the audience, and the purpose
is answerable, and holding the draft hostage to detail the user did not think
to supply fails a request that could have been met. The user can fill a marked
gap in seconds; they cannot fill one they were never shown.

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

**Location.** Where a persistent local filesystem exists, the cache is
`$HOME/writing-style/`, created `chmod 700` on first use -- in plain sight
rather than buried in a cache path, because it is meant to be read and edited
by hand, and deliberately not a shared temp path, since these files hold
observations derived from private correspondence.

`$HOME` means whatever the environment reports, read from it directly; a
session can legitimately run with it set somewhere other than the account's
usual home. **Where this goes wrong is the handoff to a tool that needs an
absolute path.** Reading `$HOME` in a shell and creating the directory there is
the easy half; then a file-writing tool wants a full path and the conventional
`/Users/<name>` form gets substituted from habit, so the directory is created
in the right place and the files land somewhere else entirely. **Paste the
exact string `$HOME` expanded to, the one just printed**, and never a path
assembled from a username, from a directory further up the working tree, or
from any other absolute path that happens to be visible. If you are about to
type `/Users/` or `/home/` into a file path, stop: that is the mistake, and it
is invisible afterwards because the shell half was correct.

Writing to the wrong home puts this user's private observations somewhere that
is not theirs and leaves the profile unwritten, so the next session redoes the
research and nobody knows why.

Where nothing persists -- an ephemeral container included -- keep the profile
in the session and offer it at the end as a block the user can paste somewhere
durable, saying plainly that it was not saved. Never copy it to cloud storage
or anywhere else off the machine.

Contents:

```
identity.md                       Who the user is, in identifiers
general.md                        What holds true across every card
index.md                          Searches already run and what they returned
card-<medium>-<audience-slug>.md  One style card per (medium, audience) pair
```

**A channel is an audience in its own right**, slugged by its own name and id (`card-slack-platform-eng-C024BE91L.md`), never by a category such as `private-channel`. See [references/finding-samples.md](references/finding-samples.md).

All four formats are in
[references/cache-files.md](references/cache-files.md). Read it before writing
any of these files, and before relying on what one of them says. In short:
`identity.md` records the account identifiers that decide which samples are
the user's, plus their org, team, and known relationships; `general.md`
records only the traits that survive every audience, which is what a request
with no card of its own falls back to; `index.md` is the ledger of searches
already run, including the ones that came back empty.

The one format detail the rules below depend on: a stored card carries a
`Ledger:` block recording the samples its counts were derived from, with a
date on each. That is what lets a card be extended rather than rebuilt, and
what lets its counts be split into a recent reading and an all-time one
without re-reading the corpus. A card with no ledger can still be used; it
just cannot be split, and counts as all-time only until the next refresh
builds one.

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
- **Confirm a hit cheaply, do not rebuild it.** Every reuse earns exactly one
  search for samples newer than the card's newest, and no more. If that turns
  up nothing, use the card as it stands. If it turns up a few, fold them into
  the ledger, update the counts, and re-bucket. Re-reading the whole corpus a
  card was built from defeats the point of having cached it. This single
  bounded search is what keeps a card current, which is why it runs on every
  reuse rather than on a timer.
- A partial hit is a starting point, not an answer. Same person, different
  medium means the relationship read carries over and the mechanics do not:
  keep the audience findings, research the medium fresh.
- Corpus notes are reusable across cards. A sample found while building one
  card counts as evidence for another if it matches that card's scope.
- **Age never invalidates a card, so do not expire one.** Cards are kept and
  extended indefinitely; what ages is the recent window, not the card. A card
  with neither a ledger nor a `Built:` line has no provenance and gets rebuilt
  rather than trusted.
- **Validate a card that has passed a year, rather than rebuilding it.**
  Re-confirm the relationship class against `identity.md`, and re-run blame on
  one or two of its samples. Why these two rules rather than an expiry date is
  in [references/cache-files.md](references/cache-files.md), under *Why cards
  are kept rather than expired*.
- **Drift invalidates a card regardless of age.** When the relationship
  recorded on the card contradicts what `identity.md` or a directory now says
  (the card reads peer, the user has since recorded them as a manager), the
  register the card describes is the wrong one. Rebuild it, and say why the
  cached one was not used rather than silently swapping it out.
- New samples extend a card rather than replacing it. Re-running research adds
  the messages written since, appends them to the card's ledger, and updates
  the counts.
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

**Then apply the recency cap, before writing the confidence down.** The table
counts evidence without asking when any of it was written, so a card built from
plentiful but old samples lands on High and stays there unless something else
intervenes. Check the recent window (Step 6) and cap accordingly:

- **No samples in the last twelve months:** cap at medium, or at low if the
  table already said medium.
- **One or two:** keep the table's value, and say recent coverage is thin.

Evidence about a period that has ended is a weaker claim about today than the
same counts drawn from current samples, and a card that says `high` without
qualification is not making the weaker claim.

Extract only what the samples actually show. Every claim on the style card must
be traceable to a count ("first name only, 7 of 9 samples"), not to an
impression.

**Two thresholds decide what earns a line.** A positive claim needs a
numerator, a negative claim needs a denominator, and the asymmetry is
deliberate: a positive entry puts words into the draft and risks pastiche,
while a negative entry only filters and can invent nothing.

| Claim | Requirement |
|---|---|
| **Positive** (attested, prefers) | 3 or more samples, and at least a third of the corpus |
| **Negative** (absent, avoid) | a corpus of 5 or more samples, no occurrence minimum |

Three samples out of two hundred is real but not characteristic, and two out
of four is too few to trust. An absence observed across two samples is not
evidence of an absence.

**Structure:** typical length in words or lines, paragraph count and size,
whether the ask comes first or last, use of bullets versus prose, headers,
whether context precedes or follows the point.

**Openers and closers:** greeting form or absence, sign-off form or absence,
name form used for the recipient, self-reference.

**Sentences:** median length, variance, fragments, questions, imperatives,
starting words and connectives.

**Vocabulary.** Record this in slots rather than as a list of words, using the
seven slots in [references/style-card.md](references/style-card.md): `marker`,
`hedge`, `stance`, `term`, `shorthand`, `filler`, `avoid`. Fixing the slots is
what makes the reading specific without making it long -- the ceiling is set by
the slot count rather than by however much the corpus holds -- and an empty slot
is itself a finding.

Every positive entry carries one attested snippet. "heads up" on its own loses
the frame, and a bare opener, a mid-sentence aside, and an apology softener are
three different habits. The snippet is also what makes the entry checkable the
next time the card is extended.

**Tone:** directness, warmth markers, humor and its type, apology and gratitude
habits, how disagreement and bad news get delivered.

**Mechanics:** capitalization, punctuation habits (em dashes, semicolons,
ellipses, exclamation marks), contractions, Oxford comma, formatting,
deliberate typos or shorthand.

**Emoji and reactions:** which ones recur, where they sit (inline, trailing, as
a reaction instead of a reply), and how dense they are per message. Note the
audiences that get none, since that boundary is usually sharp and a stray
emoji in the wrong register is one of the loudest tells there is.

**Platform conventions.** Mentions, links, images, threading, and formatting:
learned habits rather than prose style, and getting them wrong reads as
"someone else's account" faster than a wrong adjective does. Count them the
same way. What to look for in each is in
[references/finding-samples.md](references/finding-samples.md); read it when
the medium has conventions at all, which chat and trackers do and plain email
largely does not.

**Polish tier**, from the four-tier ladder in
[references/style-card.md](references/style-card.md): fire-off, quick note,
considered, or formal. The tier comes from the samples, not from the topic's
importance. Where the current situation differs from every sample -- bad news
to someone the user only ever jokes with, a first message to a new client --
say so and confirm the tier before drafting.

---

## Step 6: Present the Style Card

Show the card, then the draft, in the same reply.

**The card fixes the order, it does not withhold the draft.** The user asked
for an artifact; a reply carrying only a style card delivers none of it and
spends a turn on saying so. Leading with the reading still buys the cheap
correction the card exists for -- they can fix how they were read rather than
patch a draft built on it -- and they can do that with the draft already in
hand. Ask the question, then draft under the answer you expect, and say that is
what you did.

Hold the draft back only when the card cannot be built at all: no audience to
scope it to (Step 1), or no usable evidence and no description to work from
(below). A gap in what the message should *say* is not one of those cases; mark
it and draft, as Step 1 describes. This is the reference the
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

Opening:     <observed pattern>              <recent> | <all time>
Structure:   <length, ordering, formatting>   <recent> | <all time>
Sentences:   <length, rhythm, fragments>
Vocabulary:
  marker     attested  <observation>          <recent> | <all time>
                       > <attested snippet>
  term       prefers   <observation>          <recent> | <all time>
                       > <attested snippet>
  hedge      absent    <observation>          <all time>
  <slot>     <status>  <observation>          <recent> | <all time>
                       > <attested snippet, on every attested and prefers entry>
Tone:        <directness, warmth, humor, how hard things get said>
Mechanics:   <capitalization, punctuation, contractions>
Emoji:       <which, where, how dense, and to whom none are sent>
Conventions: <mentions vs written names, links, screenshots, threading>
Closing:     <observed pattern>               <recent> | <all time>
Avoid:       <structural and mechanical tells absent from every sample>

Gaps:        <what the samples do not cover for this request>
Ledger:      <N> samples, <oldest date> -> <newest date>
Confirmed:   <date of last delta search> | relationship re-checked <date> |
             reused from cache, built <date> | rebuilt
```

**Every vocabulary entry carries four things**, and an entry missing any of
them is not finished:

1. Its **slot name** from the Step 5 table, one slot per line. Do not merge
   several slots onto one line; `hedge/filler/apology absent throughout` hides
   three separate findings and can carry only one count.
2. A **status**: `attested`, `prefers`, or `absent`.
3. A **count**, on every entry including the absences. `absent throughout` is
   an impression; `0 of 8` is an observation.
4. An **attested snippet**, on every `attested` and `prefers` entry, quoted
   from a sample. A bare word or a parenthetical example is not a snippet: the
   frame is the finding, and `"heads up"` alone does not say whether it opens
   the message or sits mid-sentence.

This holds however the card is rendered. Whenever the block gets reformatted
into prose or into a table cell, the slot names go first, the counts and
snippets follow, and what is left is the impression this skill exists to
replace.

Ask: "Does this match how you'd write it? Anything to adjust before I draft?"

### Counts carry two horizons

A card built from a ledger reports what the recent samples show and what the
whole corpus shows:

```
Opening:  "hey Jordan," lowercase   8 of 8 (2025-09 -> 2026-08) | 22 of 24 since 2023-04
```

Every counted line carries the observation, **a count** (always -- a line
without one has dropped back to the impression this skill exists to replace),
and **both figures whenever the horizons differ**. Recent is the last twelve
months; split the counts when three or more samples fall inside it, and the
recent figure is then the reading. Fewer than three, or none, and the card uses
the all-time figure and says so -- an empty recent window also caps confidence
at medium.

Dropping the older figure once the horizons disagree is the one thing that is
never right: the disagreement *is* the finding, and it is the user's to settle
("you used to say ticket, the last eight say issue, which is current?").

The window rules, the four precedence cases, and why these are counted buckets
rather than decay weights are in
[references/style-card.md](references/style-card.md); the ledger format that
makes any of it possible is in
[references/cache-files.md](references/cache-files.md), with the rest of the
cache formats. Read them before rendering a card from a ledger, or writing one.

### Write the card to the cache

Write it when the card is built, not at the end of the run. A card that is only
narrated is a card the next session has to rebuild from scratch, which is the
entire cost this cache exists to avoid.

1. Write `card-<medium>-<audience-slug>.md`: the card block above, plus the
   ledger.
2. Add or update this card's row in `index.md`, including any search that came
   back empty.
3. Rebuild `general.md` if this card is new or changed.

**Say what you actually wrote, and nothing more.** "Cached at
`~/writing-style/card-...md`" is a claim about the filesystem, and it is false
unless that file is now there. Do not report a save you did not perform, and do
not report one you only intended: a user told the research was cached will not
think to ask for it again, so the next session pays the full research cost with
nobody aware of why. If the write fails, or the environment has no persistent
disk (Step 2, case 2), say so plainly and offer the profile as a block the user
can paste somewhere durable.

**This is not the rule about placing the artifact.** Step 7 forbids saving the
*draft* into a mailbox, tracker, or channel without being asked, and being told
the user is unavailable never authorizes that. The cache is this skill's own
working memory, in the user's own home directory, and writing it is expected on
every run that builds or changes a card. The two rules point in opposite
directions on purpose: never place the artifact, always persist the profile.

### When there is no usable evidence

Say so plainly. Do not fill the gap with a generic professional voice and do
not present an unevidenced card as if it were researched. Report what was
searched and what came back empty, fall back to `general.md` if the cache has
one, and ask the user to describe how it should sound in their own words --
"blunt, no greeting, two lines" beats any ladder of options. Label the result
for what it is: `Confidence: none, user-described`, or `low, cross-medium` when
it leaned on `general.md`.

The full path, including what `general.md` can and cannot tell you and how to
handle an explicit skip-the-research override, is in
[references/finding-samples.md](references/finding-samples.md).

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

**Present it, do not place it.** The draft goes in the reply. It does not get
saved as a mail draft, posted, or written into a tracker, however convenient
that would be and however clearly the user has said they are unavailable. If
the medium has a natural home for it, say the text is unsaved and offer to put
it there; that offer costs one line and leaves the decision where it belongs.

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
- **The draft stays in the conversation until the user says otherwise.** Never
  send or post it, and do not save it into their mailbox, chat client, tracker,
  or any other external system without their explicit say-so on the text you
  are about to write. Once they agree, save it and tell them where it landed.
- **Being told the user is unavailable is not permission to write.** It
  authorizes drafting without a confirmation pause, never touching an external
  system: they cannot correct a draft they never saw (Step 7).
- Keep excerpts on the style card short, only long enough to evidence a claim.
- Do not carry content from someone else's message into the deliverable, and do
  not quote a third party's writing as the user's own style.
- Corpus material stays in the cache and out of the deliverable, the
  repository, and any commit. The cache is the user's own directory, holds
  derived observations rather than copies of correspondence, and is theirs to
  delete: say where it lives the first time this skill writes to it.

---

## Before sending the draft

Three checks, because each catches something that survives every earlier step:

- **Did a card come before the draft?** A draft that appears without one has
  skipped the step that makes it sound like the user.
- **Does every claim on the card trace to a sample actually read?** No claim
  stated more confidently than its evidence supports.
- **Did any content come from the samples rather than the request?** Style is
  copied; content never is.

The rest of what would go in a checklist here is already stated where it
applies: audience in Step 1, cache identity in Step 2, rungs and authorship in
Step 4, thresholds in Step 5, the tells list in Step 7, corrections in Step 8.
Restating them at the end taught nothing and drifted out of step with the
originals.
