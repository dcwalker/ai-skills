# Sizing and Tiers

The signal tables behind Step 3's two assessments — is this personal or
professional work, and how big is it — and the tier they select between. The
tier decides how much enrichment an item gets for the rest of the run, so read
this when an item's context or size is not obvious from the first glance.

## Agreeing a pace on a large set (Step 1a)

At 15+ items, propose a pace before starting, and say why it is not a
shortcut:

> "This set has 42 items. I'll still review each one individually and confirm
> every change before applying it, that's the point, but I'll work similar
> items together (by sender, list, or label) and summarize and confirm
> proposals every 10 items instead of one giant summary at the end. Sound
> right?"

Grouping does not replace the processing order (Step 1b); it comes first, and
the order is applied within it. Items keep the chosen order inside each group,
and each group sits where its earliest item falls in that order. With an inbox
going oldest first, a sender whose first thread is the oldest in the inbox is
worked first, even if its other threads are the newest.

## Batch actions (Step 1a)

A batch action is one change (a label, a move, an archive) applied to several
items in a group at once. It is proposed and confirmed like any other change.

**Membership.** Each item's own listing details (subject and snippet, or title
and description), not just the shared sender or label, must justify its place
in the batch. A thread that shares a sender with promotional mail but reports
an unrecognized charge does not belong in an archive batch with the promotions.

**After it is applied**, check each item in the batch against the scope again:

- An item the action moved out of scope (archived out of the inbox, moved off
  the list being triaged, closed) is finished.
- An item still in scope is presented to the user individually for triage,
  with its own entry and its own proposed changes in the Step 9 summary, as if
  the batch had not happened. A batch action never counts as its triage.

**Presenting it in Step 9.** The batch gets one entry that names every item in
it by link, or by its exact title or subject when no link is available, so the
user can pull one out before confirming. A summary description ("9 promotional
emails", "survey, webinar invite, ...") does not name the items. The entry also
says whether the action takes those items out of scope. Items it leaves in
scope get their own per-item entries as well; an entry such as "12 threads
labeled Finance" never stands in for them.

**Batches in sequence.** Items a first batch leaves in scope can be finished by
a later batch that moves them out of scope. After a Finance label on every
Harbor Bank thread, the nine promotional mailers can go into one archive batch,
presented as one entry naming all nine. What cannot happen is an item staying
in scope with no entry of its own: a list of items under one shared decision
("Applies to: ...", "same treatment") that leaves them in scope is group
triage, not individual review.

## 3a. Work context

| Context | Signals |
|---|---|
| **Personal** | Personal board, no team members, items like "buy groceries", "plan trip", "call dentist"; personal email account |
| **Professional** | Team board/project, issue types like Bug/Story/Epic, sprint context, business terminology; work email account |
| **Mixed** | Personal productivity board used for work tasks, or a team board with personal to-dos mixed in; a single inbox that receives both |

## 3b. Task size

| Size | Signals |
|---|---|
| **Small** | Single clear action, completable in under a day, no dependencies, obvious done state. For email, a single reply or a single follow-up. |
| **Medium** | Multiple steps or sub-tasks, 1–5 days of effort, may have a dependency or two |
| **Large / Project** | Multi-week or multi-phase effort, has sub-tasks or should have them, involves multiple people or systems |

## 3c. Select enrichment tier

Use the context and size to select the right enrichment level. The goal is
*just enough structure to move the item forward*, no more.

| Tier | When | What to enrich |
|---|---|---|
| **1 — Lightweight** | Personal + Small, or any pure personal quick-task, or a short email that needs only a reply or a delete | Title/subject clarity, assignee (if shared), due date (if time-sensitive), maybe a brief note |
| **2 — Standard** | Professional + Small/Medium, or Personal + Medium/Large, or an email that needs to be captured as an action | Title, description outcome, labels, assignee, priority, due date |
| **3 — Full** | Professional + Large, or any item that is clearly a project or initiative | Everything in Tier 2, plus phases/sub-tasks, external links, and effort estimate |

When in doubt, start at a lower tier. It is always better to under-enrich and
ask than to impose structure the user didn't want.
