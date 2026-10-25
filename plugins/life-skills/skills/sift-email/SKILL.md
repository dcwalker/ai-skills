---
name: sift-email
description: "Bulk-label new Gmail by importance in one unattended pass, guided by a living rubric in Claude Docs that learns from the user's edits and from how the user handles the mail. No per-item review, and it never stops to ask, so it can run as a scheduled routine. It runs only when called directly, with /sift-email or by a routine that reads this file, never on its own. For interactive, one-by-one processing of emails, cards, or tickets, use triage instead."
disable-model-invocation: true
metadata:
  category: life-skills
---

# Sift Email

Label new Gmail by importance in a single pass, without stopping to review items
with the user. The point is that the user glances at labels later, not that they
sit through a session now. Every action is a visible, reversible label, mark,
or star, so a wrong call costs one glance, and how the user handles the mail
afterward makes later runs better.

Sift is built to run unattended, usually as a scheduled routine. Nobody is
there to answer a question mid-run, so sift never blocks: when something is
unclear it takes the safe default, finishes the run, and leaves the question
where the user will see it (see [Never block](#never-block)).

Two voices, by where the line goes. **Inside the rubric**, its rules, table
rows, and About me notes speak as the user, as the rest of the doc does, so
the document reads as one voice: "Price-increase notices I don't want are
Bulk". **Everywhere else sift reports what it did** (the log, changelog
entries, comments, and its reply), it names the user or says "you", never
"I", "me", "my", "the user", or a pronoun ("they" included): "asks Pat to
confirm whether Pat can run the table", or "asks you to confirm".

Sessions have no memory of each other. Everything that carries forward lives in
Gmail, which holds each thread's priority and star, and in two Claude Docs:
the rubric (rules and examples) and the log (what sift decided, when, and
why).

## Labels

Sift uses Gmail's own Important mark and star, which mail clients already
show, and three labels of its own, nested under `AI/` so they never mix with
the user's.

| Priority | How sift applies it |
|---|---|
| Important | Gmail's Important mark (system label `IMPORTANT`) |
| Low priority | `AI/Low priority` |
| Bulk | `AI/Bulk` |
| Junk | `AI/Junk` |

What each priority means, and which mail gets it, is the rubric's to say: its
Labels table and its rule sections. Every thread sift evaluates gets exactly
one priority. Gmail marks some
threads Important on its own when they arrive, so sift removes that mark from
every thread it calls something else. When someone is waiting on the user
specifically, sift also stars the thread (system label `STARRED`). Sift never
removes a star, its own included: the user clears stars.

**Tabs.** Sift also files each thread it evaluates into the inbox tab the
rubric's Tabs table gives, including where Important mail and anything the
table doesn't place go (Primary, when it doesn't say). The tab is a call of
its own, apart from priority and labels, so a Bulk thread can be in Social and
one newsletter in Updates while another is in Promotions. Gmail's own sort
carries no weight: when a thread is in another tab, move it. Move a thread by
adding its tab's label
(`CATEGORY_PERSONAL` for Primary, `CATEGORY_SOCIAL`, `CATEGORY_PROMOTIONS`, or
`CATEGORY_UPDATES`); Gmail removes the old one.

Create any missing `AI/` labels on the first run. Never create other labels,
archive, mark read, mute, trash, or move mail out of the inbox (a tab keeps it
in the inbox), so nothing sift does can hide a message. The rubric's
Permissions section may grant more.

**The user's edits stand.** When a thread's priority, star, or tab differs from
what the log says sift last applied, the user changed it. Sift keeps it, and
doesn't learn from it, though a new message that needs a reply still gets a
star. A new reply can arrive with Gmail's own Important mark or tab, so either
is the user's only when a message from before sift's call carries it and the
log shows otherwise (Step 5 fetches the thread to check).

When the rubric asks for a label of its own, in its Labels table or
Permissions section, such as "label event invitations as invitation", create
it under `AI/` in title case, `AI/Invitation`, never as a bare `invitation`
beside the user's own labels. Apply it alongside the thread's priority, never
in place of one. Decide by what the message is, as the rubric describes
it, not by whether it uses a particular word: a message asking where a receipt
is does not get `AI/Receipt`. A label sift starts using gets a row in the
Labels table, saying when sift applies it, in the same run.

Label changes take label IDs, and `label:` searches take label names: quote a
name with a space (`label:"AI/Low priority"`) or write its spaces and `/` as
`-` (`label:AI-Low-priority`). List the labels once at the start of a run and
use the IDs from then on.

## Step 1: Find the rubric and log

Claude Docs has no search by title, so the docs are found by link. The routine
prompt (or the user's request) gives the links to the `Email Sift Rubric` and
`Email Sift Log` docs. Reach each by its link with the docs connector, and only
that way: never fetch a doc link on the web. Don't read either doc whole yet.

If no links were given, create the rubric from `references/rubric-template.md`
and the log from `references/log-template.md`, exactly as the templates read:
leave the Timezone line for the user to set rather than guessing it. Put both
links at the top of the summary, with a line asking the user to add them to the routine prompt so later
runs reuse the same docs, and to skim the starter rubric. The routine prompt is
the only place a later run will find them, so don't save them anywhere else,
such as a memory file. Never guess at an existing doc, and never create a
second pair when links were given.

If a link does not open, or the docs connector is missing, keep going: label
every inbox thread (`in:inbox`, as if the log had no run) by the rules in
`references/rubric-template.md`, skip every doc update, and say in the summary
which doc could not be opened or which connector to turn on. A missing doc is
never a reason to stop the run, ask, or wait for the user. Don't
try to open a doc link any other way, such as fetching it on the web.

Before the first doc edit in a run, read the docs connector's own guide for
how to edit blocks and comment, rather than guessing the call shapes.

Unless Step 2 ends the run, read the whole rubric before Step 3. It is the
user's own definition of importance, so where
it disagrees with your instincts, follow the rubric. The rubric's Timezone line
names the user's timezone, and every date and time sift writes is the run's
date and time in that timezone (Step 2 says how to read it).

**The rubric is one living document, and sift keeps all of it accurate**: the
how-to, the Labels table, About me, every rule section, Newsletters, Tabs, and
Examples. Each rule sits in the section it belongs to, so the doc never gives
two answers to one question. Sift edits any section to place what it learns,
to merge or reword overlapping rules without changing what they say, and to
keep the Labels table matching the labels sift applies, category labels
included. It never adds to Permissions or Notify: those say what sift may do,
and only the user grants that.

- **Markers.** A line sift writes from evidence carries a marker and a date:
  `(inferred)` for a fact under About me, `(observed)` for a rule from the
  daily review, `(learned)` for a Newsletters line. The user's lines and the
  rules from their answers carry none. A user's edit to a marked line is the
  latest word on it.
- **Evidence wins.** When the evidence contradicts a rule, whoever wrote it,
  rewrite that rule to match, mark it `(observed)`, and put its old wording in
  the changelog entry.
- **Older rubrics.** A rubric with an Added by sift section, from an earlier
  template, has its rules moved into the sections they belong to and that
  section removed, once, in Step 3.
- **Placeholders.** A line wholly in parentheses, such as `- (I add these)`,
  is replaced by the first real entry in its place.

## Step 2: Check whether there is anything to do

Most scheduled runs find nothing new, so check that cheaply before reading the
rubric. A first run, with no doc links given, always has work: skip to Step 3.

From the log, read only the newest run heading, for the last run's start
time, and whether a "Daily review: <date>" line carries the run's date; from
the rubric, only its Timezone line. Get each with a search of the doc, never
a whole-doc read: reading the rubric whole comes after these checks find work.

Then read the system clock once, in that timezone (for example,
`TZ=<the Timezone line's zone> date '+%Y-%m-%d %H:%M %s'`), for the run's
date, time, and epoch seconds. Every date or time sift writes this run uses
it: the log heading and lines, the "nothing new" line, changelog entries,
About me dates, and the check for whether a note's end date has passed.
Never use the machine's own local date, the date your environment reports,
or a message's date: near midnight they fall on a different day than the
user's. A first run, which skips this step, reads the clock the same way in
the starter rubric's timezone.

Each run heading (Step 7) holds that run's start, so mail arriving during a
run, or after one that failed before its heading, is still found. A heading
without epoch seconds is searched from its date (`after:<YYYY/MM/DD>`).

Then run each of these checks once. Each needs only a single search or query,
and the first result answers it:

- Mail since the last run: `in:inbox after:<the last run's epoch seconds>`,
  counting only a thread the log doesn't name or whose newest message is
  later than its newest log line. When the log has no run yet, any inbox
  thread at all is work.
- The daily review is due: the log has no "Daily review" line dated the
  run's date (see Step 4).
- A comment thread on the rubric whose latest comment is the user's (see
  [Never block](#never-block)).

If every check comes back empty, the run has nothing to do. Don't read the rest
of the rubric or tidy it. Add one line to the log's Runs section, "<date> <time>:
nothing new", or, when the newest line of exactly that form is from the run's
date, update its time instead; a run's summary is never such a line. Never
edit a run heading: the next run searches from it. Say "Nothing new" in chat,
and stop.

## Step 3: Tidy the rubric

Do this on every run, before anything else touches the rubric, even when no
mail is new. Go through these six checks in order, and fix each one that
fails. A fresh-looking rubric is not a reason to skip them: read the actual
headings and lines.

1. **Expired notes.** Under About me, remove each `(inferred)` line whose end
   date has passed or whose sender has not written in 180 days.
2. **One heading per subject.** Under About me, if two headings cover the same
   subject (`### Soccer` and `### Kids' soccer`), merge them into one and move
   every note from both under it.
3. **Notes under the right heading.** Under About me, move each note that sits
   under the wrong heading, or apart from the notes about the same person,
   team, or event, so it sits with them. Check every line, the user's own
   included, and "Right now:" lines too: a line about the school's auction
   belongs under the school's heading even though it is time-limited. Move
   lines and drop nothing.
4. **Every rule in its place.** Move a rule that sits in the wrong section,
   merge rules that say the same thing, and settle two rules that disagree in
   favor of the newer evidence. In a rubric with an Added by sift section,
   move each of its rules into the section it belongs to, remove the section,
   and rewrite the intro and How to use text that describe the old split, as
   `references/rubric-template.md` words them.
5. **Tables current.** Compare the Labels table with the label list fetched
   at the start of the run: every `AI/` label in the account has a row saying
   when sift applies it, category labels included, and a label sift no longer
   applies says so in its row rather than disappearing. Gmail's Important mark
   and the star have rows too. The Tabs table has one row per inbox
   tab Gmail offers: list the labels once, and add a row for any `CATEGORY_*`
   tab the table lacks, saying it holds nothing until the user says what
   goes there.
6. **Size.** If the rubric outside About me runs past roughly two pages, or
   the changelog past 20 entries, consolidate it as
   [Keeping the rubric healthy](#keeping-the-rubric-healthy) describes:
   merge overlapping rules, trim the examples to the most instructive, and
   keep the newest 20 changelog entries, counting the one this step adds.

Record what this step changed in one changelog entry dated the run's date,
such as "Reorganized About me: merged Soccer into Kids' soccer, moved two
notes". When all six checks pass, the step changes nothing and adds no
entry. About me notes the rest of the run adds or removes go in one changelog
entry for the run, such as "Added About me notes on the U12 assistant coach
and the landlord".

## Step 4: Learn

Do this before labeling, so today's run benefits from what the user did since
the last one. The user corrects sift in the rubric; this step adds the rest.

**Answered questions first.** Read the comment threads sift opened on the
rubric (see [Never block](#never-block)). Sift's comments carry the user's
name, the same as the user's own, so every comment sift writes starts with
`Sift:`, and a comment without it is the user's. A thread whose latest
comment is the user's is an answer. Apply it as a rubric change in the section
it belongs to, unmarked since it is the user's word, relabel the
thread the question was about if the answer settles it, then reply in that
thread saying what changed. That reply, starting `Sift:`, marks the
answer as applied.

**Daily review.** When the log has no "Daily review" line dated the run's
date, read how the user handled the threads sift labeled 1 to 7 days before
the run. Take each thread the log's lines name in that window and that no
`observed` line names yet, fetch its labels and messages (metadata only),
and look for these signals, compared against what the log says sift applied:

| Sift applied | What the user did since | Suggests |
|---|---|---|
| Bulk or Junk | Replied in the thread, or starred it | Low priority |
| Low priority | Replied in the thread, or starred it | Important |
| Important | Archived it while still unread | Low priority |

A star or reply counts only when the thread's log line shows no star (Step 7),
since a reply to a thread sift starred is expected. Nothing else is a signal:
opening, reading, archiving read mail, leaving a thread alone, or changing its
priority (the user's edits stand) says nothing.

Record each signal under this run's heading in the log (Step 7):
`observed | <thread id> | <sender> | sift applied <label> | <what the user did> | suggests <label>`.
Then count, for each sender with a new signal, the `observed` lines the log
holds for that sender. When 3 or more of that sender's threads suggest the
same label and none suggests a different one, add one rule to the section for
that priority, or update the rule already there for that sender:
`(observed) <sender>: <suggested priority> | <n> threads: <what the user did> | <run's date>`.
A newsletter goes in the Newsletters section instead (see
[Newsletters](#newsletters)). The rule changes no thread's labels: the user
has already dealt with those threads. When it contradicts a rule already in
the rubric, rewrite that rule instead (Evidence wins, in Step 1).

Write `Daily review: <run's date>, <n> threads checked, <n> signals` under
this run's heading, even with no signals, so later runs that day skip it.

**Every rubric change** this step makes is the smallest one that would have
produced the right call: an example, or a rule in its section. Name the
senders the evidence shows, or the narrowest category that covers them
("automated deadline notices from the club registrar"), never a wider class
such as all vendors or all community organizations. Note each change in the
rubric's changelog with the run's date (from Step 2, not the date of the mail
or the answer that prompted it). The changelog records rubric changes only;
an opened question goes in the run summary.

## Step 5: Gather new mail

Search `in:inbox after:<the last run's epoch seconds>` (Step 2 says what to
search from when the heading has none). When the log has no run yet, search
`in:inbox`: the first run labels the whole inbox, however old. Sort each
thread found:

- **New:** the log doesn't name it. Evaluate it.
- **New reply:** the log names it, and its newest message is later than its
  newest log line. Fetch the thread with its messages first, before any label
  change, and compare the messages from before sift's last call with what the
  log says it applied. A priority, star, Important mark, or tab on those
  messages that differs from the log is the user's: keep it, and decide only
  what the user didn't change (see [Labels](#labels)).
- **Already done:** the log names it, and nothing has arrived since. Skip it.

Process every match in this run: follow the search's next-page token until
there is none, never stopping at the first page.

Fetch metadata only (sender, recipients, subject, date, snippet, existing
labels). Read a full body only when the metadata can't settle the call, such as
a snippet that points to "see attached" or a portal.

If nothing matches, write a run summary reporting zero (Step 8) and stop.

## Step 6: Label

For each thread, decide using the rubric, then what is known about the sender
and the message.

**Who the sender is.** Before looking anyone up, go through every sender in
this run and settle which ones About me already covers; look up only the rest,
even when looking several up at once. Then for each sender, in this order:

1. **Check About me first.** If it already says who this sender is, use that
   and do no lookup for them this run. The user's own About me lines carry the
   rubric's weight, so a "right now" priority they wrote decides like a rule;
   `(inferred)` lines are context.
2. **Otherwise look them up,** with the questions below.
3. **Record what you learned before moving on:** add an `(inferred)` line under
   the matching topic in About me (see [About me](#about-me)), with no account,
   card, order, or ID number in it, or any part of one. When the lookups found
   nothing about the sender, no note is needed.

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
  sender's earlier mail, or under the user's receipts label. What a purchase
  changes about the call is the rubric's to say.

**What the message is:**

- What labels does the thread already carry? The user's own labels (often
  applied by filters on arrival), a star, and the Important mark and tab Gmail
  gives on arrival are context like every other signal here. They can help
  explain a message, but none of them decides the call: the rubric does.
- Is the user in To rather than Cc, or the only recipient?
- Does it mention a date, deadline, or event in the next week?
- Is it a reply in a thread the user started?

These often separate "important" from "urgent-sounding" better than the text
itself. Marketing copy says "action required"; a coach's two-line note doesn't.

**Mass mail or mail meant for the user.** Mass mail is sent to a list rather
than to the user personally. The signs are a no-reply sender, an unsubscribe
link, and the user missing from To or a list address in To; Gmail's tab is
not one. Only when those leave it unclear, read the raw message for
`List-Unsubscribe` or `List-Id` headers. Whether it is mass mail is a fact
about the message; which priority that earns is the rubric's to say, in its
priority sections.

A newsletter is placed by the rubric's Newsletters section rather than by its
mass-mail signals, since every newsletter carries them, and gets the
newsletter category label when the Labels table names one.

Choose exactly one priority. A star for needs reply can accompany any of them,
and depends on the message, not the sender: star the thread when the message
meets the rubric's Needs reply section. When the rubric leaves a call between
two priorities open, follow its When torn section; when it has none, choose
the less severe priority.

Apply the call at the thread level, leaving one priority: for Important, add
`IMPORTANT` and remove any `AI/` priority label; for the others, add that
label and remove `IMPORTANT` and any other `AI/` priority label. Then add
`STARRED` when a message sift hasn't evaluated before needs a reply and the
thread has no star: a star the user removed stays off until a new message
needs one. Never remove a star. Then file the thread into its tab (see
[Labels](#labels)) unless it is already there. Keep whatever else the user
changed, and batch the calls where the tools allow.

Then carry out whatever the rubric's Permissions section grants for the
priority just applied, such as archiving a thread labeled `AI/Junk` when Permissions
says so, or adding a label the rubric asks for (under `AI/`, as
[Labels](#labels) describes), and nothing it doesn't grant. A grant applies on every run, without
asking.

## Step 7: Log

Under the log's Runs section, after its intro and above the newest run, add
this run's heading as exactly `### <date> <time> (<epoch seconds>)`, from the
clock in Step 2: a `###` heading, never bold text or another level, since the
next run searches from it. Write the heading first, directly above the
previous newest run's heading, so the Runs section stays newest first; every
run that has work writes one. Then add one line per thread evaluated. On a run
that created the docs, the summary under that heading (Step 8) starts with both
docs' links.

`<time> | <thread id> | <sender> | <subject> | <applied> | <one-sentence reason>`

Never use a message's timestamp or a made-up time. `<applied>` names the
priority (`Important`, `AI/Low priority`, `AI/Bulk`, or `AI/Junk`), then
`starred` when sift added the star or `star kept` when the thread already had
one, then the tab (`Primary`, `Social`, `Promotions`, or `Updates`), then any
category label; where the user's edit stood, say so. The log is
the only record of what sift has seen and applied. The reason is how the user
audits a call later, so make it specific: "Coach asking for carpool
volunteers by Friday" beats "Seems important."

**Log lines report, so they name the user.** Every line sift writes in the log
(reasons, the summary, `observed` and Daily review lines) and every changelog
entry names the user or says "you", even when it restates a rubric rule
written as "I": "nothing asked of Pat", not "nothing asked of me"; "not on
Pat's Valued list", not "not on my Valued list". No log line holds an
account, card, order, or ID number, or any part of one.

Keep the log to the last 30 days. When older entries exist, replace them with a
one-line summary per week (counts by priority, stars added, rules learned).

## Step 8: Summarize

Before writing the summary, go through this checklist. It is not optional: for
each item this run has not done, do it now, then continue.

- Step 3's four checks all pass now: no expired `(inferred)` line, no two
  About me headings for one subject, no note under the wrong heading, and the
  rubric within its size limits.
- Every sender whose lookup found something has an `(inferred)` note, and no
  sender About me already covered was looked up.
- Every action the Permissions section grants was carried out.
- On a run that created the docs, the log summary carries both doc links.

Write the run summary directly under this run's heading in the log, above its
thread lines, then repeat it in chat:

- Counts: processed, important, low priority, bulk, junk, starred, and moved
  to each tab, taken from what was actually applied this run.
- The important and starred threads, one line each with the reason.
- The daily review's line, when it ran, and the rubric changes it produced.
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
grant belongs in the rubric's Permissions section. Do not offer to do it, or
to add the grant yourself: Permissions is the user's to write. Beyond the log
and this reply, send no push notification or message about a run, whatever
tools exist, except one per thread the rubric's Notify section describes,
naming its sender and subject. A missing or empty Notify means none.

## Never block

When a run needs the user's judgment, it does not wait for it:

1. Take the safe default. For an unclear new thread, apply the rubric's When
   torn section (Step 6). For evidence too thin or mixed to settle a rule,
   change nothing until the user answers.
2. Open a comment on the rubric doc, anchored on the rule or example it is
   about (or the doc's title when none fits). Start it with `Sift:`, name the
   thread by sender, subject, and date, say what sift did, and ask one
   specific question.
3. List the question in the run summary.

The next run reads the user's replies in Step 4 and applies them. Don't open
a second comment for a question that already has an open one, and don't put
the question, or any offer to do more, at the end of the reply: the run ends on
its summary.

## About me

The rubric's About me section is sift's memory between runs, shared with the
user and grouped under topic headings (`### Kids' soccer`, `### Home`) so
related notes sit together. Step 3 applies the grouping and expiry rules below
at the start of every run.

- **Write what you learn.** After a lookup tells you who a sender is, or the
  user's own mail shows what matters to them now (an event they keep writing
  about, a sale they are running), add one line under the topic it belongs
  to, next to the notes it most relates to (the same person, team, or event)
  rather than at the end, creating the heading when none fits:
  `(inferred) <fact> | <source> | <date learned>`, the date learned being the
  run's date from Step 2, for example
  `(inferred) jordan.lee@riversideunited.example coaches the U12 team | Contacts | 2026-10-10`.
  A fact with an end date says so ("until November 1"). Never record an
  account, card, order, or ID number, or any part of one.
- **Keep it accurate.** Correct or update any line when sift learns better,
  keeping `(inferred)` on what it infers. When the user edits an inferred
  line, take the edit as a correction; when they remove `(inferred)`, the line
  reads as the user's statement.
- **Keep it grouped.** Each topic heading holds the notes about one subject,
  and related notes sit next to each other within it. When a note sits under
  the wrong topic or apart from its related notes, move it; when two headings
  cover the same subject, merge them. Nothing is dropped. Note a
  reorganization, and every note added or removed, in the changelog.
- **Keep it current.** Remove an inferred line once its end date has passed,
  or once its sender has not written in 180 days. Re-check a sourced fact
  older than 90 days before relying on it, and update its date. Past about
  200 inferred lines, remove the ones unused the longest.

## Newsletters

The rubric's Newsletters section lists, by name and sender, the newsletters
the user wants to read under Valued and the rest under Not valued. Read it on
every run, so the user's edits take effect on the next run. Match by sender or
name; a newsletter on neither list is Not valued.

Sift adds a line from the daily review (Step 4), once a newsletter reaches its
threshold, under Valued: `(learned) <newsletter name> | <sender> | observed
<date>`, with the run's date from Step 2. When the newsletter is on the Not
valued list, move its line to Valued, marked the same way. Note each line
added or moved in the changelog.

## Keeping the rubric healthy

The rubric is read in full on every run, so it has to stay short. About me
follows its own upkeep above; when the rest grows past roughly two pages,
consolidate overlapping rules wherever they sit and keep only the most
instructive examples. A consolidated rule covers no more than the rules it
replaces: it names the same senders they named, with no open-ended category
such as "and similar" or "other vendors". The changelog keeps the last 20
entries, this run's included, newest first.

## Running it as a routine

Sift is meant to run on a schedule. For the setup a Claude Code cloud routine
needs (connectors, the repository checkout it reads this skill from, the doc
links in its prompt, and the schedule), see
`references/running-as-a-routine.md`.
