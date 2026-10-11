---
name: sift-email
description: "Bulk-label new Gmail by importance in one unattended pass, guided by a living rubric doc in Google Drive that learns from the user's corrections. No per-item review. Use whenever the user asks to sift, sort, or label new mail, or wants to know what's important without going through it themselves: \"sift my email\", \"sift my inbox\", \"run sift\", \"label my new mail\", \"what's important in my inbox\", \"flag anything important since this morning\", \"check my corrections\". For interactive, one-by-one processing of emails, cards, or tickets, use triage instead."
metadata:
  category: life-skills
---

# Sift Email

Label new Gmail by importance in a single pass, without stopping to review items
with the user. The point is that the user glances at labels later, not that they
sit through a session now. Every action is a visible, reversible label, so a
wrong call costs one glance and one correction, and each correction makes the
next run better.

Sessions have no memory of each other. Everything that carries forward lives in
two places, and this skill reads and writes both on every run:

- **Gmail labels** hold the working state: what has been processed, what was
  labeled, and what the user corrected.
- **Two Google Docs** hold the judgment: the rubric (rules and examples) and the
  log (what was decided and why).

## Labels

All AI labels are nested under `AI/` so they never mix with the user's own.

| Label | Meaning |
|---|---|
| `AI/Important` | The user would want to see this today |
| `AI/Low priority` | Nothing urgent; fine to read later or never |
| `AI/Needs reply` | Someone is waiting on the user specifically |
| `AI/Wrong` | Applied by the user to flag a bad call |

Every thread sift evaluates gets exactly one of `AI/Important` or
`AI/Low priority`. `AI/Needs reply` is added on top of either when it applies.
This means a thread with neither priority label has not been processed, so the labels themselves are the record
of what sift has seen and no separate marker is needed.

Create any missing labels on the first run. Never create other labels, archive,
mark read, mute, trash, or move mail. Sift only adds and removes `AI/` labels,
so nothing it does can hide a message. The user may later grant more for specific
categories; that grant lives in the rubric, not here.

## Step 1: Load the rubric and log

Search Drive by exact title, not by URL, so the skill works from any account
connected to the same Google account:

- `Email Sift Rubric`
- `Email Sift Log`

Before editing either doc, read the google-workspace skill and its Docs
reference. Editing an existing Google Doc requires the Google Docs connector;
Drive alone can create files but not change them. If the Docs connector is
missing, still run the labeling, then say in the summary that rubric and log
updates were skipped and which connector to turn on.

If the rubric doesn't exist, create it from `references/rubric-template.md` and
the log from `references/log-template.md`, then tell the user in the summary
that a starter rubric was created and they should skim it.

Read the whole rubric. It is the user's own definition of importance, so where
it disagrees with your instincts, follow the rubric.

## Step 2: Learn from corrections

Do this before labeling, so today's run benefits from yesterday's feedback.

Find corrections from the last 14 days:

- **Explicit:** threads with `label:AI/Wrong`.
- **Changed:** threads the log shows sift labeled that now carry a different
  priority label (the user swapped it), or that gained or lost
  `AI/Needs reply`.
- **Removed:** threads the log shows sift labeled that now carry no priority
  label at all. Treat a removed `AI/Important` as "should have been low
  priority" unless the context says otherwise.

Removed labels need care: an unlabeled thread looks unprocessed, so Step 3
would pick it up again. Resolve every removal here first and relabel it
according to the corrected rubric, so the same wrong call is never reapplied.

For each correction, work out what the user meant. Usually it's clear from
the sender, subject, and what was changed. Turn it into the smallest rubric
change that would have produced the right call: add an example, sharpen a rule,
or add a sender or topic. Prefer generalizing ("automated deadline notices from
the club registrar") over memorizing one email, but don't generalize past what
the evidence supports.

If a correction is genuinely ambiguous, don't guess and don't stop. Collect it
as a question for the summary, and leave the rubric alone for that item.

After handling a correction, remove `AI/Wrong` from the thread and note the
change in the rubric's changelog with the date.

## Step 3: Gather new mail

Query: `in:inbox newer_than:7d -label:AI/Important -label:"AI/Low priority"`

The priority labels are the cursor, so no "last run" timestamp is needed. A
new reply in an already processed thread arrives without a label, so the
thread resurfaces and gets re-evaluated with the new message in view, which is
what you want.

Fetch metadata only (sender, recipients, subject, date, snippet, existing
labels). Read a full body only when the metadata can't settle the call, such as
a snippet that points to "see attached" or a portal.

If nothing matches, the run is complete. Report zero and stop.

## Step 4: Label

For each thread, decide using the rubric, then these signals where available:

- Has the user written to this sender before? (`from:me to:<sender>`)
- Is the sender in the user's contacts?
- Is the user in To rather than Cc, or the only recipient?
- Does it mention a date, deadline, or event in the next week?
- Is it a reply in a thread the user started?

These often separate "important" from "urgent-sounding" better than the text
itself. Marketing copy says "action required"; a coach's two-line note doesn't.

Choose exactly one priority label. `AI/Needs reply` can accompany either.
When a re-evaluated thread's priority changes, remove the old priority label so
only one remains. When torn between important and low priority, choose
important: a
false alarm is visible and costs a glance, while a miss blends into the inbox
and may never be noticed.

Apply labels at the thread level. Batch the
calls where the tools allow.

## Step 5: Log

Append one line per thread to the log under today's date heading:

`<time> | <sender> | <subject> | <labels applied> | <one-sentence reason>`

The reason is how the user audits a call later, so make it specific: "Coach
asking for carpool volunteers by Friday" beats "Seems important."

Keep the log to the last 30 days. When older entries exist, replace them with a
one-line summary per week (counts by label, corrections received).

## Step 6: Summarize

Close with a short summary in chat:

- Counts: processed, important, low priority, needs reply.
- The important and needs-reply threads, one line each with the reason.
- Corrections learned and the rubric changes they produced.
- Any questions about ambiguous corrections.
- Anything skipped (missing connector, doc not found).

Keep it scannable. The user should be able to read it in under a minute.

## Keeping the rubric healthy

The rubric is read in full on every run, so it has to stay short. When it grows
past roughly two pages, consolidate overlapping rules and keep only the most
instructive examples. Never delete a rule the user wrote by hand; rewrite only
rules sift added. The changelog keeps the last 20 entries.
