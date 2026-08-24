# Cache files

Reference for the `writing` skill, Step 2: the format of every file in the
style cache. `identity.md` and `general.md` are written and edited by hand;
style cards and `index.md` are generated per request. The rules for deciding
when to reuse a cached card and when to research again live in SKILL.md,
because they are read on every run.

## identity.md

The single most useful thing in the cache. Authorship matching needs the
user's account identifiers, relationship inference needs their team and org,
and both are otherwise rediscovered from scratch every session. Written once,
edited by hand whenever something changes:

```markdown
# Identity

Name:       <full name>, and any other form that appears as a display name
Mail:       <address>, <alias>, <alias>
Chat:       <workspace>: <user id> (@<handle>)
Code host:  <github/gitlab/bitbucket handle>
Tracker:    <jira/linear account id>
Org:        <employer>, <primary email domain>
Team:       <team name>, <how the team is named in the directory or tracker>

Former:     <identifier> until <date> — <what it was>
Last verified: <date>

## Relationships

<name or address>: <class> — <note>
```

Rules for identity.md:

- **The user's declarations win over inference.** A relationship recorded here
  is the answer; the relationship signals in SKILL.md Step 4 only fill what it does not cover. If a
  directory contradicts it, say so rather than silently overriding either.
- **It is a matcher, not a claim about the world.** Use the identifiers to
  decide which samples are the user's. Do not use the file's contents as facts
  in a draft.
- **Verify on read, and stamp it.** Compare the recorded identifiers against
  the accounts this session is actually connected to. When they agree, update
  `Last verified`. When one no longer resolves, or an account reports an
  identifier the file does not have, say so once and offer to update the file.
  A file with no `Last verified` date has never been checked, which is worth
  knowing before leaning on it.
- **Never delete a superseded identifier, retire it.** An address or handle
  that changed still owns everything written under it, and the older corpus is
  only findable by searching for it. Move it to `Former:` with the date it
  stopped being current, and keep searching both. Deleting it silently shrinks
  the evidence for every card built afterwards.
- **A team change ages the relationships, not the identifiers.** Classes
  derived from team membership stop being reliable the moment the team
  changes: yesterday's peers may now be another team, and the manager
  relationship has usually moved. Re-derive the classes rather than trusting
  the recorded ones, and treat the affected cards under the drift rule in
  SKILL.md Step 2.
- **An employer change ages nearly everything audience-shaped.** The
  professional corpus belongs to a former context: those recipients are no
  longer being written to, and the register that suited them may not transfer
  to their counterparts at the new place. `general.md` survives, since it
  describes the person rather than the audience. Cards for work audiences do
  not, and should be rebuilt from samples at the new employer rather than
  carried across.
- **Offer to write it, do not assume it.** On the first run, discover what the
  connected accounts report, show the user what would be recorded, and write
  it only if they agree. It persists, and it is theirs.
- **Identifiers only.** Never passwords, tokens, API keys, or session
  cookies. Nothing in this file should be a credential.

## general.md

The traits that hold no matter who the user is writing to. Registers differ
wildly by audience, but a few habits survive every one of them, and those are
what make an unfamiliar situation still sound like the same person. This is
the fallback when a request has no card and no samples behind it.

```markdown
# General style

Holds across <N> cards, spanning <which audiences>.

<trait>  — <n of N cards> — <the evidence, briefly>
```

Rules for it:

- **A trait qualifies only by surviving contrast.** It has to hold across a
  majority of the cards, or three of them, whichever is greater, and those
  cards must cover two different relationship classes. A habit visible only in
  work email is a fact about work email.
- **The bar rises as the cache grows.** Three cards' agreement is a strong
  claim when there are four cards and a weak one when there are fifteen, which
  is why the threshold is a proportion rather than a fixed count. Accumulation
  should make this file stricter, not merely longer.
- **Rebuild it whenever a card is added or changed**, and drop any trait the
  new card contradicts. Two cards' worth of agreement is a coincidence.
- **Expect it to be short.** Punctuation habits, a few recurring words, how
  bad news gets delivered, whether the point comes first, and length instincts
  relative to the medium. Greetings, sign-offs, and formality almost never
  qualify, because those are exactly what audience changes.
- **It is rung 5 evidence, cached.** Label it that way when it is used: it
  says how the user writes in general, never how they write to this person.

## Style cards

A stored card is the Step 6 block **plus a ledger**, which is the one part not
shown to the user. The card is the reading; the ledger is the evidence it was
read from:

```
Ledger:      <N> samples, <oldest date> -> <newest date>
Confirmed:   <date of last delta search> | relationship re-checked <date> |
             reused from cache | rebuilt

## Ledger
| id | date | source | used for |
|---|---|---|---|
| <message id> | 2026-07-30 | sent mail | opening, marker, closing |
```

The ledger is what makes a card permanent. Without it, extending a card means
re-reading the corpus, and the only affordable alternative is throwing the card
away and starting again. With it, a refresh searches for samples newer than the
newest row, appends them, and re-counts. A card can then be carried and
sharpened for years.

Rules for the ledger:

- **Identifiers, dates, and the short snippets already on the card. Never
  message bodies.** This is the same constraint the rest of the cache is under,
  and the ledger is the file most tempted to break it.
- **Rows are appended, never rewritten.** A count that moves should be
  explicable by rows added since, and that only holds if the old rows stay put.
- **`Confirmed:` is not an expiry date.** It records when the card last went
  looking for newer samples, which is what tells a reader whether the recent
  window is thin because the user has gone quiet or because nobody has checked.
- **A card with no ledger is still usable.** Treat it as all-time only, do not
  split its counts, and build a ledger on the next refresh rather than
  discarding the reading. Cards written before ledgers existed are in this
  state, and they are not stale, merely unsplittable.

## index.md

The searches ledger, one row per card, so a later session can tell what was
already looked for without opening every card:

```markdown
| medium | audience | samples | rung | confidence | newest sample | confirmed |
|---|---|---|---|---|---|---|
| email | peer (jordan@example.com) | 6 | 1 | high | 2026-07-30 | 2026-08-02 |
| slack | #platform-eng (C024BE91L) | 14 | 1 | high | 2026-08-01 | 2026-08-02 |

Searches run: `in:sent to:jordan@example.com` (6 results, 2026-08-02)

No samples found for: text message, any personal audience.
```

The "no samples found for" line matters as much as the rows. A search that
came back empty is a result worth keeping, so the next session does not spend
the same calls rediscovering that the corpus is not there.

## Why cards are kept rather than expired

The analysis is the expensive part of this skill and voice changes slowly, so a
card is kept and extended indefinitely rather than aged out. What ages is not
the card but its recent window: samples fall out of it with the passage of time
alone, the recent counts thin, and an empty recent window lowers confidence
rather than discarding the reading.

That is also why a card past a year gets validated rather than rebuilt.
Re-confirming the relationship class and re-running blame on a sample or two is
seconds of work, and it is the price of keeping a card forever: a card that is
only ever extended inherits any contamination it started with and compounds it
rather than washing it out.
