# Cache files

Reference for the `writing` skill, Step 2. These are the two files in the
style cache that a person writes and reads by hand, rather than ones the
skill generates per request. Style cards and `index.md` are generated, and
their formats stay in SKILL.md.

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
- **Verify before trusting a stale entry.** An identifier that matches no
  connected account is worth mentioning once; accounts get renamed.
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
