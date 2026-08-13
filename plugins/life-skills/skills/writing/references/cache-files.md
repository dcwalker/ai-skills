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

- **A trait qualifies only by surviving contrast.** It has to hold across at
  least three cards covering two different relationship classes. A habit
  visible only in work email is a fact about work email.
- **Rebuild it whenever a card is added or changed**, and drop any trait the
  new card contradicts. Two cards' worth of agreement is a coincidence.
- **Expect it to be short.** Punctuation habits, a few recurring words, how
  bad news gets delivered, whether the point comes first, and length instincts
  relative to the medium. Greetings, sign-offs, and formality almost never
  qualify, because those are exactly what audience changes.
- **It is rung 5 evidence, cached.** Label it that way when it is used: it
  says how the user writes in general, never how they write to this person.

## Style cards

A stored card is the Step 6 block verbatim, including its `Built:` line. That
line is the only record of how old a reading is, so a card written without it
cannot be aged, refreshed, or honestly reused:

```
Built:       <date written> | newest sample <date> | rebuilt | reused from cache
```

Age is measured from the newest sample rather than the build date. A card
rebuilt yesterday out of samples that all predate last spring is stale in the
way that matters, because it describes how the user wrote a year ago. The
build date is for telling the user how old the reading is when it gets reused.

## index.md

The searches ledger, one row per card, so a later session can tell what was
already looked for without opening every card:

```markdown
| medium | audience | samples | rung | confidence | newest sample | built |
|---|---|---|---|---|---|---|
| email | peer (jordan@example.com) | 6 | 1 | high | 2026-07-30 | 2026-08-02 |

Searches run: `in:sent to:jordan@example.com` (6 results, 2026-08-02)

No samples found for: text message, any personal audience.
```

The "no samples found for" line matters as much as the rows. A search that
came back empty is a result worth keeping, so the next session does not spend
the same calls rediscovering that the corpus is not there.
