---
name: sift-email
description: "Bulk-label new Gmail by importance in one unattended pass, guided by a living rubric in Claude Docs that learns from the user's corrections. No per-item review, and it never stops to ask, so it can run as a scheduled routine. Use whenever the user asks to sift, sort, or label new mail, or wants to know what's important without going through it themselves: \"sift my email\", \"sift my inbox\", \"run sift\", \"label my new mail\", \"what's important in my inbox\", \"flag anything important since this morning\", \"check my corrections\". For interactive, one-by-one processing of emails, cards, or tickets, use triage instead."
metadata:
  category: life-skills
---

# Sift Email

Label new Gmail by importance in a single pass, without stopping to review items
with the user. The point is that the user glances at labels later, not that they
sit through a session now. Every action is a visible, reversible label, so a
wrong call costs one glance and one correction, and each correction makes the
next run better.

Sift is built to run unattended, usually as a scheduled routine. Nobody is
there to answer a question mid-run, so sift never blocks: when something is
unclear it takes the safe default, finishes the run, and leaves the question
where the user will see it (see [Never block](#never-block)).

Wherever sift writes, in the log, the rubric, a comment, or its reply, it
refers to the user only by name or as "you", never with a pronoun, "they"
included: "asks Pat to confirm whether Pat can run the table", or "asks you
to confirm".

Sessions have no memory of each other. Everything that carries forward lives in
two places, and this skill reads and writes both on every run:

- **Gmail labels** hold the working state: what has been processed, what was
  labeled, and what the user corrected.
- **Two Claude Docs** hold the judgment: the rubric (rules and examples) and the
  log (what was decided and why).

## Labels

All AI labels are nested under `AI/` so they never mix with the user's own.

| Label | Meaning |
|---|---|
| `AI/Important` | The user would want to see this today |
| `AI/Low priority` | Legitimate mail with nothing urgent; fine to read later or never |
| `AI/Junk` | Unsolicited marketing, spam-like, or mail the user never wants |
| `AI/Needs reply` | Someone is waiting on the user specifically |
| `AI/Sifted` | Sift has evaluated this thread |
| `AI/Wrong` | Applied by the user to flag a bad call |

Every thread sift evaluates gets `AI/Sifted` and exactly one priority label:
`AI/Important`, `AI/Low priority`, or `AI/Junk`. `AI/Needs reply` is added on
top of any of them when it applies. `AI/Sifted` is the record of what sift has
seen, so a thread that carries it but no priority label is one the user
removed a label from (Step 2).

Gmail labels a whole thread, including messages that arrive later, so a new
reply in a sifted thread already carries the old labels. Step 3 finds those
replies by date instead.

Create any missing labels on the first run. Never create other labels, archive,
mark read, mute, trash, or move mail. Sift only adds and removes `AI/` labels,
so nothing it does can hide a message. The user may later grant more for specific
categories; that grant lives in the rubric, not here.

Searches and label changes take label IDs, not names. List the labels once at
the start of a run and use the IDs from then on.

## Step 1: Load the rubric and log

Claude Docs has no search by title, so the docs are found by link. The routine
prompt (or the user's request) gives the links to the `Email Sift Rubric` and
`Email Sift Log` docs. Open each by its link with the docs connector, and only
that way: never fetch a doc link on the web.

If no links were given, create the rubric from `references/rubric-template.md`
and the log from `references/log-template.md`, exactly as the templates read:
leave the Timezone line for the user to set rather than guessing it. Put both
links at the top of the summary, with a line asking the user to add them to the routine prompt so later
runs reuse the same docs, and to skim the starter rubric. The routine prompt is
the only place a later run will find them, so don't save them anywhere else,
such as a memory file. Never guess at an existing doc, and never create a
second pair when links were given.

If a link does not open, or the docs connector is missing, still run the
labeling with the starter rubric's rules, skip every doc update, and say in the
summary which doc could not be opened or which connector to turn on. Don't try
to open a doc link any other way, such as fetching it on the web.

Before the first doc edit in a run, read the docs connector's own guide for
how to edit blocks and comment, rather than guessing the call shapes.

Read the whole rubric. It is the user's own definition of importance, so where
it disagrees with your instincts, follow the rubric. The rubric's header names
the user's timezone; use it for every time sift writes.

Everything above the rubric's **Added by sift** section is the user's: the
how-to, the label key, the About me notes, and the user's rules. Sift never
rewords, moves, or removes any of it, with two exceptions: lines under About
me that start with `(inferred)` are sift's own (see [About me](#about-me)), and
a template placeholder, a line wholly in parentheses such as `- (I add these)`
or `### (topic, such as Kids' soccer, Home, or Work)`, may be replaced by the
first real entry in its place. Its own rules go under Added by sift, each one
learned from the user's corrections, so a sift rule may narrow one of the
user's rules for exactly the cases its corrections cover, and no further.

Before moving on, tidy About me as [About me](#about-me) describes: remove
`(inferred)` lines whose end date has passed or whose sender has gone quiet.
If the rest of the rubric runs past roughly two pages, or the changelog past 20
entries, consolidate it this run as
[Keeping the rubric healthy](#keeping-the-rubric-healthy) describes.

## Step 2: Learn from corrections

Do this before labeling, so today's run benefits from yesterday's feedback.

**Answered questions first.** Read the comment threads sift opened on the
rubric (see [Never block](#never-block)). Sift's comments carry the user's
name, the same as the user's own, so every comment sift writes starts with
`Sift:`, and a comment without it is the user's. A thread whose latest
comment is the user's is an answer. Apply it as a rubric change, relabel the
thread the question was about if the answer settles it, then reply in that
thread saying what changed. That reply, starting `Sift:`, marks the
answer as applied.

**Label corrections.** Find corrections from the last 14 days:

- **Explicit:** threads with `label:AI/Wrong`.
- **Added:** a thread carrying two priority labels, or a priority label that
  the log shows sift did not apply. The label the user added is the answer,
  and the one sift applied was wrong. Remove sift's label.
- **Changed:** threads the log shows sift labeled that now carry a different
  priority label (the user swapped it), or that gained or lost
  `AI/Needs reply`. A change to `AI/Needs reply` corrects that label only.
- **Removed:** threads with `AI/Sifted` and no priority label.

When the user's own label gives the answer, use it. When it does not
(`AI/Wrong` alone, or a removed label), read the direction from what sift had
applied, which the log records:

| Sift applied | Correct label |
|---|---|
| `AI/Important` | `AI/Low priority` |
| `AI/Junk` | `AI/Low priority` |
| `AI/Low priority` | Unclear: could be Important or Junk |

When the direction is unclear, leave the thread's labels as they are and open
a question (see [Never block](#never-block)). Relabel every other correction now,
so the same wrong call is never reapplied.

For each correction, work out what the user meant. Usually it's clear from
the sender, subject, and what was changed. Turn it into the smallest rubric
change that would have produced the right call: add an example, or add or
sharpen a rule under Added by sift. When the user's own rule produced the wrong
call, leave it as written and add a sift rule naming the exception. Prefer
generalizing over memorizing one email, but name the senders the corrections
show, or the narrowest category that covers them ("automated deadline notices
from the club registrar"), never a wider class the evidence doesn't show, such
as all vendors or all community organizations.

If a correction is genuinely ambiguous, don't guess and don't stop. Open it
as a question, and leave the rubric alone for that item.

After handling a correction, remove `AI/Wrong` from the thread and note the
change in the rubric's changelog with the run's date (today, not the date of
the mail or the answer that prompted it). The changelog records rubric
changes only; an opened question goes in the run summary, not the changelog.

## Step 3: Gather new mail

Two searches, using label IDs:

- **New threads:** `in:inbox -label:<AI/Sifted id>`, every inbox thread sift
  has not evaluated, however old. A first run labels the whole inbox.
- **New replies:** `in:inbox label:<AI/Sifted id> after:<date of the last run>`,
  where the last run's date is the newest run summary in the log. Keep only
  threads whose newest message is later than that run, and re-evaluate them
  with the new message in view.

Process every match in this run. A search returns one page at a time, so
follow each search's next-page token until there is none; never stop at the
first page.

Fetch metadata only (sender, recipients, subject, date, snippet, existing
labels). Read a full body only when the metadata can't settle the call, such as
a snippet that points to "see attached" or a portal.

If nothing matches, write a run summary reporting zero (Step 6) and stop.
The summary still matters: the next run's new-reply search starts from its
date.

## Step 4: Label

For each thread, decide using the rubric, then what is known about the sender
and the message.

**Who the sender is.** For each sender, in this order:

1. **Check About me first.** If it already says who this sender is, use that
   and do no lookup for them this run. The user's own About me lines carry the
   rubric's weight, so a "right now" priority they wrote decides like a rule;
   `(inferred)` lines are context.
2. **Otherwise look them up,** with the questions below.
3. **Record what you learned before moving on:** add an `(inferred)` line under
   the matching topic in About me (see [About me](#about-me)). When the lookups
   found nothing about the sender, no note is needed.

The lookups:

- Is the sender in the user's contacts? A contact's groups, organization, and
  relationships often say who they are (a coach, a teacher, a family member).
- Has the user written to this sender before? (`from:me to:<sender>`)
- What labels do the sender's earlier threads carry? Many are applied by the
  user's own filters and name the sender's category (a school, a club, a
  utility, receipts). Search those labels for similar messages, and look at
  how the user treated them and how the rubric's examples label them.
- Is it tied to something the user actually bought, or from a company they
  ordered from recently? Check before you say so: find the order in the
  sender's earlier mail, or under the user's receipts label. When it is, the
  message is not unsolicited, even when it reads like marketing: a review
  request or order follow-up from such a sender is Low priority, not Junk.

**What the message is:**

- What labels does the thread already carry? The user's own labels (often
  applied by filters on arrival), a star, and Gmail's own Important marker are
  context like every other signal here. They can help explain a message, but
  none of them decides the call: the rubric does.
- Is the user in To rather than Cc, or the only recipient?
- Does it mention a date, deadline, or event in the next week?
- Is it a reply in a thread the user started?

These often separate "important" from "urgent-sounding" better than the text
itself. Marketing copy says "action required"; a coach's two-line note doesn't.

Choose exactly one priority label. `AI/Needs reply` can accompany any of them,
and depends on the message, not the sender: add it when the message itself asks
the user something or needs their acknowledgment, as the rubric's Needs reply
section defines. A message to a group that only informs, or a reply that only
acknowledges the user's own message ("ok, thanks"), needs no reply.
When a re-evaluated thread's priority changes, remove the old priority label so
only one remains. When torn, choose the less severe call:

- Between important and low priority, choose important. A false alarm is
  visible and costs a glance, while a miss blends into the inbox and may never
  be noticed.
- Between low priority and junk, choose low priority. Junk is for mail the user
  never wants; legitimate mail that is merely dull belongs in low priority.

Add `AI/Sifted` to every thread evaluated. Apply labels at the thread level.
Batch the calls where the tools allow.

Then carry out whatever the rubric's Permissions section grants for the label
just applied, such as archiving a thread labeled `AI/Junk` when Permissions
says so, and nothing it doesn't grant. A grant applies on every run, without
asking.

## Step 5: Log

Under the log's Runs section, add a heading for this run (its date and time,
newest run first), then one line per thread:

`<time> | <thread id> | <sender> | <subject> | <labels applied> | <one-sentence reason>`

The time is when the run started, read from the system clock (for example,
with `date`) and converted to the rubric's timezone. Never use a message's
timestamp or a made-up time. The thread id is what Step 2 uses to
tell which labels sift applied. The reason is how the user audits a call
later, so make it specific: "Coach asking for carpool volunteers by Friday"
beats "Seems important."

Keep the log to the last 30 days. When older entries exist, replace them with a
one-line summary per week (counts by label, corrections received).

## Step 6: Summarize

Before writing the summary, check that this run did all of these, and finish
any it missed:

- About me was tidied at the start (Step 1).
- Every sender whose lookup found something has an `(inferred)` note, and no
  sender About me already covered was looked up again.
- Every action the Permissions section grants was carried out.
- A rubric past roughly two pages, or a changelog past 20 entries, was
  consolidated.

Write the run summary directly under this run's heading in the log, above its
thread lines, then repeat it in chat:

- Counts: processed, important, low priority, junk, needs reply, taken from
  the labels actually applied this run.
- The important and needs-reply threads, one line each with the reason.
- Corrections learned and the rubric changes they produced.
- Questions opened, and answers applied.
- Actions taken under a Permissions grant, such as threads archived.
- Anything skipped (missing connector, doc not opened).
- On a run that created the docs, their links first, in the log summary as
  well as in chat.

Keep it scannable. The user should be able to read it in under a minute. A
scheduled run's chat output may have no reader, which is why the log carries
it too. For the same reason, end on the summary, never on an offer or a
question: anything that needs the user's answer is a comment on the rubric
(see [Never block](#never-block)). When the request asked for an action the
rubric does not grant, such as archiving, say it was not done and that the
grant belongs in the rubric's Permissions section.

## Never block

When a run needs the user's judgment, it does not wait for it:

1. Take the safe default. For an unclear correction, keep the thread's current
   labels, `AI/Wrong` included, until the user answers. For an unclear new
   thread, apply the tie-breaking rules in Step 4.
2. Open a comment on the rubric doc, anchored on the rule or example it is
   about (or the doc's title when none fits). Start it with `Sift:`, name the
   thread by sender, subject, and date, say what sift did, and ask one
   specific question.
3. List the question in the run summary.

The next run reads the user's replies in Step 2 and applies them. Don't open
a second comment for a question that already has an open one, and don't put
the question, or any offer to do more, at the end of the reply: the run ends on
its summary.

## About me

The rubric's About me section is sift's memory between runs, shared with the
user and grouped under topic headings (`### Kids' soccer`, `### Home`) so
related notes sit together.

- **Write what you learn.** After a lookup tells you who a sender is, or the
  user's own mail shows what matters to them now (an event they keep writing
  about, a sale they are running), add one line under the topic it belongs
  to, creating the heading when none fits:
  `(inferred) <fact> | <source> | <date learned>`, for example
  `(inferred) jordan.lee@riversideunited.example coaches the U12 team | Contacts | 2026-10-10`.
  A fact with an end date says so ("until November 1").
- **Edit only `(inferred)` lines.** Every other line is the user's. When the
  user edits an inferred line, take the edit as a correction; when they remove
  `(inferred)`, the line is theirs from then on.
- **Keep it current.** Remove an inferred line once its end date has passed,
  or once its sender has not written in 180 days. Re-check a sourced fact
  older than 90 days before relying on it, and update its date. Past about
  200 inferred lines, remove the ones unused the longest.

## Keeping the rubric healthy

The rubric is read in full on every run, so it has to stay short. About me
follows its own upkeep above; when the rest grows past roughly two pages, consolidate overlapping rules under Added by sift and
keep only the most instructive examples. A consolidated rule covers no more
than the rules it replaces: it names the same senders they named, with no
open-ended category such as "and similar" or "other vendors". Never touch a rule above Added by sift. The
changelog keeps the last 20 entries, this run's included, newest first.

## Running it as a routine

Sift is meant to run on a schedule. For the setup a Claude Code cloud routine
needs (connectors, the doc links in its prompt, the plugin install, and the
schedule), see `references/running-as-a-routine.md`.
