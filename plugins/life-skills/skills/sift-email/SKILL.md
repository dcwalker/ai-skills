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
`Email Sift Log` docs. Open each by its link.

If no links were given, create the rubric from `references/rubric-template.md`
and the log from `references/log-template.md`. Put both links at the top of the
summary, with a line asking the user to add them to the routine prompt so later
runs reuse the same docs, and to skim the starter rubric. Never guess at an
existing doc, and never create a second pair when links were given.

If a link does not open, or the docs connector is missing, still run the
labeling with the starter rubric's rules, skip every doc update, and say in the
summary which doc could not be opened or which connector to turn on.

Before the first doc edit in a run, read the docs connector's own guide for
how to edit blocks and comment, rather than guessing the call shapes.

Read the whole rubric. It is the user's own definition of importance, so where
it disagrees with your instincts, follow the rubric. The rubric's header names
the user's timezone; use it for every time sift writes.

## Step 2: Learn from corrections

Do this before labeling, so today's run benefits from yesterday's feedback.

**Answered questions first.** Read the comment threads sift opened on the
rubric (see [Never block](#never-block)). Sift's comments carry the user's
name, the same as the user's own, so every comment sift writes starts with
`Sift:`, and a comment without it is the user's. A thread whose latest
comment is the user's is an answer. Apply it as a rubric change, then reply
in that thread saying what changed. That reply, starting `Sift:`, marks the
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
change that would have produced the right call: add an example, sharpen a rule,
or add a sender or topic. Prefer generalizing ("automated deadline notices from
the club registrar") over memorizing one email, but don't generalize past what
the evidence supports.

If a correction is genuinely ambiguous, don't guess and don't stop. Open it
as a question, and leave the rubric alone for that item.

After handling a correction, remove `AI/Wrong` from the thread and note the
change in the rubric's changelog with the date.

## Step 3: Gather new mail

Two searches, using label IDs:

- **New threads:** `in:inbox newer_than:7d -label:<AI/Sifted id>`
- **New replies:** `in:inbox label:<AI/Sifted id> after:<date of the last run>`,
  where the last run's date is the newest run summary in the log. Keep only
  threads whose newest message is later than that run, and re-evaluate them
  with the new message in view.

Fetch metadata only (sender, recipients, subject, date, snippet, existing
labels). Read a full body only when the metadata can't settle the call, such as
a snippet that points to "see attached" or a portal.

If nothing matches, the run is complete. Report zero and stop.

## Step 4: Label

For each thread, decide using the rubric, then what is known about the sender
and the message.

**Who the sender is:**

- Is the sender in the user's contacts? A contact's groups, organization, and
  relationships often say who they are (a coach, a teacher, a family member).
- Has the user written to this sender before? (`from:me to:<sender>`)
- What labels do the sender's earlier threads carry? Many are applied by the
  user's own filters and name the sender's category (a school, a club, a
  utility, receipts). Search those labels for similar messages, and look at
  how the user treated them and how the rubric's examples label them.

**What the message is:**

- Is the user in To rather than Cc, or the only recipient?
- Does it mention a date, deadline, or event in the next week?
- Is it a reply in a thread the user started?

These often separate "important" from "urgent-sounding" better than the text
itself. Marketing copy says "action required"; a coach's two-line note doesn't.

Choose exactly one priority label. `AI/Needs reply` can accompany any of them.
When a re-evaluated thread's priority changes, remove the old priority label so
only one remains. When torn, choose the less severe call:

- Between important and low priority, choose important. A false alarm is
  visible and costs a glance, while a miss blends into the inbox and may never
  be noticed.
- Between low priority and junk, choose low priority. Junk is for mail the user
  never wants; legitimate mail that is merely dull belongs in low priority.

Add `AI/Sifted` to every thread evaluated. Apply labels at the thread level.
Batch the calls where the tools allow.

## Step 5: Log

Append one line per thread to the log under today's date heading:

`<time> | <thread id> | <sender> | <subject> | <labels applied> | <one-sentence reason>`

The time is in the rubric's timezone. The thread id is what Step 2 uses to
tell which labels sift applied. The reason is how the user audits a call
later, so make it specific: "Coach asking for carpool volunteers by Friday"
beats "Seems important."

Keep the log to the last 30 days. When older entries exist, replace them with a
one-line summary per week (counts by label, corrections received).

## Step 6: Summarize

Write the run summary at the top of the log under the run's date and time,
then repeat it in chat:

- Counts: processed, important, low priority, junk, needs reply.
- The important and needs-reply threads, one line each with the reason.
- Corrections learned and the rubric changes they produced.
- Questions opened, and answers applied.
- Anything skipped (missing connector, doc not opened).
- On a run that created the docs, their links first.

Keep it scannable. The user should be able to read it in under a minute. A
scheduled run's chat output may have no reader, which is why the log carries
it too.

## Never block

When a run needs the user's judgment, it does not wait for it:

1. Take the safe default. For an unclear correction, keep the thread's current
   labels. For an unclear new thread, apply the tie-breaking rules in Step 4.
2. Open a comment on the rubric doc, anchored on the rule or example it is
   about (or the doc's title when none fits). Start it with `Sift:`, name the
   thread by sender, subject, and date, say what sift did, and ask one
   specific question.
3. List the question in the run summary.

The next run reads the user's replies in Step 2 and applies them. Don't open
a second comment for a question that already has an open one.

## Keeping the rubric healthy

The rubric is read in full on every run, so it has to stay short. When it grows
past roughly two pages, consolidate overlapping rules and keep only the most
instructive examples. Never delete a rule the user wrote by hand; rewrite only
rules sift added. The changelog keeps the last 20 entries.

## Running it as a routine

Sift is meant to run on a schedule. For the setup a Claude Code cloud routine
needs (connectors, the doc links in its prompt, the plugin install, and the
schedule), see `references/running-as-a-routine.md`.
