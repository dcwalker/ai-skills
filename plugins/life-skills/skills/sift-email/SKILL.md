---
name: sift-email
description: "Bulk-label new Gmail by importance in one unattended pass, guided by a living rubric, kept in a private GitHub repository the user owns, that learns from the user's edits and from how the user handles the mail. No per-item review, and it never stops to ask, so it can run as a scheduled routine. It runs only when called directly, with /sift-email or by a routine that reads this file, never on its own. For interactive, one-by-one processing of emails, cards, or tickets, use triage instead."
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
unclear it takes the safe default, finishes the run, and writes the call into
the rubric where the user will see it (see [Never block](#never-block)).

Two voices, by where the line goes. **Inside the rubric**, its rules, table
rows, and About me notes speak as the user, as the rest of the doc does, so
the document reads as one voice: "Price-increase notices I don't want are
Bulk". **Everywhere else sift reports what it did** (the state file, commit
messages, changelog entries, and its reply), it names the user or says "you", never
"I", "me", "my", "the user", or a pronoun ("they" included): "asks Pat to
confirm whether Pat can run the table", or "asks you to confirm".

Sessions have no memory of each other. Everything that carries forward lives in
Gmail, which holds each thread's priority and star, and in Markdown files in
a private GitHub repository the user owns, all in its `sift-email/` folder:
`rubric.md` (rules and examples, which the user reads and edits) and one state
file per Gmail account, `state-<account>.md` (what sift has applied to each
thread in that account, and when it last ran there). Sift can run on several
of the user's Gmail accounts: the rubric describes the user, so every account
shares it, while each account keeps its own state. Each run that changes
anything ends in one commit, whose message says what sift did and why.

## Labels

Sift uses Gmail's own Important mark and star, which mail clients already
show, and three priority labels, plain top-level labels that sit among the
user's own, so the user can show or hide each one in Gmail.

| Priority | How sift applies it |
|---|---|
| Important | Gmail's Important mark (system label `IMPORTANT`) |
| Low priority | `Low priority` |
| Bulk | `Bulk` |
| Junk | `Junk` |

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

Create any of the three priority labels the account is missing on its first
run, and other labels only as the next paragraphs say. Never archive, mark read,
mute, trash, or move mail out of the inbox (a tab keeps it in the inbox), and
never rename or delete a label, so nothing sift does can hide a message or
undo the user's filing. The rubric's Permissions section may grant more.

**The user's edits stand.** When a thread's priority, star, or tab differs from
what the state file says sift last applied, the user changed it. Sift keeps it, and
doesn't learn from it, though a new message that needs a reply still gets a
star. A new reply can arrive with Gmail's own Important mark or tab, so either
is the user's only when a message from before sift's call carries it and the
state file shows otherwise (Step 5 fetches the thread to check).

**The Labels table lists every label.** The rubric's Labels table has a row
for every user label in each account sift runs on, the user's own included,
saying what goes there (Step 3 adds rows for labels that lack one). Every row
applies in every account. Apply any label whose row fits the thread, the
user's own labels included, unless its row says sift doesn't apply it, and
never one without a row. Apply it alongside the
thread's priority, never in place of one. Decide by what the message is, as
the row describes it, not by whether it uses a particular word: a message
asking where a receipt is does not get `Receipt`. Remove a label only when it
is a priority label sift is replacing; any other label may be the user's, so
it stays.

When the rubric asks for a label this account doesn't have yet, in its Labels
table or Permissions section, such as "label event invitations as
invitation", create it in title case, `Invitation`, once a thread needs it. A
row whose label exists only in another account is the same: create the label
here, with the row's name, when a thread fits the row. When a label of that
name already exists, whatever its case, use it as it is: it may be the
user's, and its row says what goes there. A label sift starts using gets a row in the Labels table,
saying when sift applies it, in the same run.

Label changes take label IDs, and `label:` searches take label names: quote a
name with a space (`label:"Low priority"`) or write its spaces and `/` as `-`
(`label:low-priority`). List the labels once at the start of a run and use the
IDs from then on.

## Step 1: Find the rubric and state

The rubric and state live in a private GitHub repository the user owns, as
`sift-email/rubric.md` and a `sift-email/state-<account>.md` for each Gmail
account. Find them by the rubric's content, never by a repository's name, and
only among the user's own repositories:

1. **Who the user is.** Run `gh api user` once for the login. It is the only
   source of the user's identity: never take one from the rubric, an email,
   a memory note, or a repository's name. Without a login, nothing below can
   be checked, so treat the files as not found.
2. **Look in this order**, stopping at the first that turns up a
   `sift-email/rubric.md` whose first line is `# Email Sift Rubric`:
   - **A saved location.** When you have persistent memory and it names the
     repository and folder, check that one first.
   - **Local checkouts.** The working directory and each directory beside it
     that is a git checkout. A cloud routine clones every repository attached
     to it there, side by side. A checkout's owner and name are the last two
     parts of its `origin` remote's path, whatever the host or proxy before
     them.
   - **A search of the user's repositories**, when the session can search:
     `gh search code '"Email Sift Rubric"' --owner <login> --filename rubric.md`.
     Always pass `--owner <login>`; never search all of GitHub, and never
     search another owner's repositories. Clone a match with
     `git clone https://github.com/<owner>/<name>` into a scratch directory
     (`$TMPDIR`), not into the user's project. A routine's session can't
     search, so it relies on its checkouts.
3. **Verify every candidate before reading it:** `gh api repos/<owner>/<name>`
   must show `owner.login` equal to the login and `private` true. A repository
   that fails either check is someone else's or public: don't read its files,
   clone it, write to it, or name its contents in the summary; say only that a
   repository was skipped and why. A saved location gets the same check.
4. **Before reading, bring the checkout up to date** with
   `git pull --ff-only`, so the user's latest edits count.

When you have persistent memory and the files were found any other way than a
saved location, save their repository and folder there, so a later run on this
machine looks there first. A saved location that fails a check or no longer
holds the rubric is replaced, never trusted.

**Which account.** The Gmail connector is signed in to one account, and its
state file is the one this run uses. Find its address from Gmail itself,
never from the rubric, a memory note, or the request:

1. Search `in:inbox`, or `in:sent` when the inbox is empty, for one thread,
   and fetch it (metadata only). Its `viewUrl` names the signed-in account as
   `authuser=<address>`; use that address.
2. When no `viewUrl` names one, search `in:sent` and fetch the newest thread
   found: the sender of the user's own message in it is the account.
3. When neither gives an address, the run can't know which state is this
   account's. When the user is there to answer, ask for the address. When no
   one is, label nothing, write nothing, and say in the summary that the
   account couldn't be identified.

Compare addresses in lowercase, and for `gmail.com` and `googlemail.com`
ignore dots and anything from a `+` in the part before the `@`, since Gmail
does: `pat.example@gmail.com` and `patexample@gmail.com` are one account.

**This account's state file** is the one in `sift-email/` whose
`Account: <address>` line names this account by that comparison, whatever its
file name. When none does:

- **An older state file.** A `sift-email/state.md` with no `Account:` line is
  from before sift ran on more than one account. Fetch one thread its Threads
  lines name (metadata only). When the thread is in this account, the file is
  this account's: add the `Account:` line and move it to
  `state-<account>.md` with `git mv`, in this run's commit. When the thread
  isn't found, or the file names no thread, leave it alone for the account it
  belongs to.
- **Otherwise** create `state-<account>.md` from
  `references/state-template.md`, with this account's address on its
  `Account:` line, in this run's commit. With no run yet, the run labels the
  whole inbox (Step 5).

The file name uses the address as found, in lowercase:
`state-pat.example@gmail.com.md`.

**Not found.** When no candidate passes, create nothing on your own:

- **When the user is there to answer** (they started this run in a
  conversation), ask which of their private repositories, and which folder,
  should hold the files, and wait for the answer before labeling anything.
  Then create `rubric.md` from `references/rubric-template.md` and this
  account's state file from `references/state-template.md` (see Which
  account), exactly as the templates read apart from the `Account:` line:
  leave the Timezone line for the user to set rather than guessing it. Commit
  and push them, then carry on with the run.
- **When no one is there to answer** (a scheduled routine, or a prompt that
  says the run is unattended), keep going: label every inbox thread
  (`in:inbox`, as if the state file had no run) by the rules in
  `references/rubric-template.md`, write nothing anywhere, and say in the
  summary that the rubric wasn't found, which repositories were skipped and
  why, and that a run started by hand will set it up. A missing rubric is
  never a reason to stop an unattended run.

If the repository can be read but a push fails for want of access, keep every
label already applied and say so in the summary.

Unless Step 2 ends the run, read the whole rubric before Step 3. It is the
user's own definition of importance, so where
it disagrees with your instincts, follow the rubric. The rubric's Timezone line
names the user's timezone, and every date and time sift writes is the run's
date and time in that timezone (Step 2 says how to read it).

**The rubric is one living document, and sift keeps all of it accurate**: the
how-to, the Labels table, About me, every rule section, Newsletters, Tabs, and
Examples. Each rule sits in the section it belongs to, so the rubric never gives
two answers to one question. Sift edits any section to place what it learns,
to merge or reword overlapping rules without changing what they say, and to
keep the Labels table listing every label in each account it runs on and
when it applies. It never adds to Permissions or Notify: those say what sift may do,
and only the user grants that.

- **Markers.** A line sift writes from evidence carries a marker and a date:
  `(inferred)` for a fact under About me or a call sift made when the rubric
  left it open (see [Never block](#never-block)), `(observed)` for a rule from
  the daily review, `(learned)` for a Newsletters line. The user's lines carry
  none. A user's edit to a marked line is the
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
rubric. A run that just created the rubric or this account's state file, or
moved an older one, always has work: skip to Step 3.

From this account's state file, read only its `Last run:` and `Daily review:` lines; from
the rubric, only its Timezone line (for example, with `grep`). Reading the
rubric whole comes after these checks find work.

Then read the system clock once, in that timezone (for example,
`TZ=<the Timezone line's zone> date '+%Y-%m-%d %H:%M %s'`), for the run's
date, time, and epoch seconds. Every date or time sift writes this run uses
it: the state file, the commit message, changelog entries, About me dates,
and the check for whether a note's end date has passed. Never use the
machine's own local date, the date your environment reports, or a message's
date: near midnight they fall on a different day than the user's. A run that
created the files reads the clock the same way in the starter rubric's
timezone.

The `Last run:` line holds the start of the last run that had work, so mail
arriving during a run, or after one that failed before saving, is still
found.

Then run each of these checks once. Each needs only a single search, and the
first result answers it:

- Mail since the last run: `in:inbox after:<the day before the last run's
  date, as YYYY/MM/DD>`. Gmail's `after:` takes only a date and returns
  nothing for epoch seconds, and its search results carry no message dates,
  so fetch each thread found (metadata only) and count it only when its
  newest message is later than the last run's epoch and, for a thread the
  state file names, later than its line's epoch. When the state file has no
  run yet, any inbox thread at all is work.
- The daily review is due: the `Daily review:` line is not the run's date
  (see Step 4).

If every check comes back empty, the run has nothing to do. Don't read the
rest of the rubric, tidy it, or change either file, and make no commit: the
next run searches from the same `Last run:` line and finds the same nothing.
Say "Nothing new" in chat, and stop.

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
   at the start of the run: every user label in this account (`labelType`
   `USER`) has a row, the user's own included (a row names a label whatever
   its case, so `travel` is covered by a `Travel` row). A row whose label this
   account lacks stays: the label may be in another account the rubric
   serves, or one sift creates here when mail fits the row, so only the user
   removes a row. For a label without a row, search the threads
   that carry it (`label:` with its name, metadata only, the newest five or
   so) and add a row starting with `(inferred)` that says what goes there, so
   sift applies it to mail like that from then on. When those threads show no
   clear pattern, or there are none, the row says sift doesn't apply the
   label until the user says when. A label sift no longer applies says so in
   its row rather than disappearing. Gmail's Important mark and the star have
   rows too. The Tabs table has one row per inbox
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

**Daily review.** When the state file's `Daily review:` line is not the run's
date, read how the user handled the threads sift labeled 1 to 7 days before
the run. Take each thread whose line in the state file falls in that window
and that no `observed` line names yet, fetch its labels and messages
(metadata only), and look for these signals, compared against what the state
file says sift applied:

| Sift applied | What the user did since | Suggests |
|---|---|---|
| Bulk or Junk | Replied in the thread, or starred it | Low priority |
| Low priority | Replied in the thread, or starred it | Important |
| Important | Archived it while still unread | Low priority |

A star or reply counts only when the thread's line shows no star (Step 7),
since a reply to a thread sift starred is expected. Nothing else is a signal:
opening, reading, archiving read mail, leaving a thread alone, or changing its
priority (the user's edits stand) says nothing.

Record each signal in the state file's Observed section (Step 7):
`<run's date> | <thread id> | <sender> | sift applied <label> | <what the user did> | suggests <label>`.
Then count, for each sender with a new signal, the Observed lines the state
file holds for that sender. When 3 or more of that sender's threads suggest the
same label and none suggests a different one, add one rule to the section for
that priority, or update the rule already there for that sender:
`(observed) <sender>: <suggested priority> | <n> threads: <what the user did> | <run's date>`.
A newsletter goes in the Newsletters section instead (see
[Newsletters](#newsletters)). The rule changes no thread's labels: the user
has already dealt with those threads. When it contradicts a rule already in
the rubric, rewrite that rule instead (Evidence wins, in Step 1).

Set the state file's line to `Daily review: <run's date>`, even with no
signals, so later runs that day skip it, and put
`Daily review: <n> threads checked, <n> signals` in the run summary.

**Every rubric change** this step makes is the smallest one that would have
produced the right call: an example, or a rule in its section. Name the
senders the evidence shows, or the narrowest category that covers them
("automated deadline notices from the club registrar"), never a wider class
such as all vendors or all community organizations. Note each change in the
rubric's changelog with the run's date (from Step 2, not the date of the mail
that prompted it).

## Step 5: Gather new mail

Search `in:inbox after:<the day before the last run's date, as YYYY/MM/DD>`,
from the state file's `Last run:` line, as in Step 2, and fetch each thread
found (metadata only) for its messages' dates. When the state file has no run
yet, search `in:inbox`: the first run labels the whole inbox, however old.
Sort each thread found:

- **Before the last run:** its newest message is no later than the last
  run's epoch. Skip it.
- **New:** the state file doesn't name it. Evaluate it.
- **New reply:** the state file names it, and its newest message is later
  than its line's epoch. Fetch the thread with its messages first, before any
  label change, and compare the messages from before sift's last call with
  what the state file says it applied. A priority, star, Important mark, or
  tab on those messages that differs from it is the user's: keep it, and decide only
  what the user didn't change (see [Labels](#labels)). Read the tab from each
  earlier message's own labels, not the thread's, since the thread shows the
  new message's tab too: an earlier message in Primary when the state file says
  Promotions means the user moved it, so file the whole thread in Primary.
- **Already done:** the state file names it, and nothing has arrived since.
  Skip it.

Process every match in this run: follow the search's next-page token until
there is none, never stopping at the first page.

Fetch metadata only (sender, recipients, subject, date, snippet, existing
labels). Read a full body only when the metadata can't settle the call, such as
a snippet that points to "see attached" or a portal.

If nothing matches, the run got this far because the daily review was due, so
it still has work to save: the tidied rubric, the daily review's changes, and
the `Daily review:` line. Skip Step 6 and go on to Step 7, which commits them
with no Threads lines, even when the review found no signals and the tidy
changed nothing.

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
`IMPORTANT` and remove any priority label (`Low priority`, `Bulk`, or
`Junk`); for the others, add that label and remove `IMPORTANT` and the other
two priority labels. Then add
`STARRED` when a message sift hasn't evaluated before needs a reply and the
thread has no star: a star the user removed stays off until a new message
needs one. Never remove a star. Then file the thread into its tab (see
[Labels](#labels)) unless it is already there. Keep whatever else the user
changed, and batch the calls where the tools allow.

Then carry out whatever the rubric's Permissions section grants for the
priority just applied, such as archiving a thread labeled `Junk` when
Permissions says so, or adding a label the rubric asks for (as
[Labels](#labels) describes), and nothing it doesn't grant. A grant applies on every run, without
asking.

## Step 7: Save the run

Update this account's state file (its layout is in
`references/state-template.md`), and no other account's:

- `Last run: <date> <time> (<epoch seconds>)`, from the clock in Step 2, the
  run's start. The next run searches from it.
- One line per thread under Threads, replacing the thread's earlier line:
  `<thread id> | <epoch seconds> | <applied>`, the epoch being this run's
  start. `<applied>` names the priority (`Important`, `Low priority`,
  `Bulk`, or `Junk`), then `starred` when sift added the star or
  `star kept` when the thread already had one, then the tab (`Primary`,
  `Social`, `Promotions`, or `Updates`), then any other label it added; where the
  user's edit stood, say `user's` after it (`Important (user's)`). The state
  file is the only record of what sift has seen and applied.
- Drop Threads lines older than 30 days and Observed lines older than 90.

Then commit `rubric.md` and the state file together in one commit and push it
to the repository's default branch. The subject is
`Sift <date> <time>: <n> threads`; the body is the run summary (Step 8),
then one line per thread evaluated:

`<thread id> | <sender> | <subject> | <applied> | <one-sentence reason>`

The reason is how the user audits a call later, through the commit history,
so make it specific: "Coach asking for carpool volunteers by Friday" beats
"Seems important." Never use a message's timestamp or a made-up time.

If the push is rejected because the remote moved (the user edited the rubric
during the run, or a run on another account saved), `git pull --rebase` and
push again. If the rebase conflicts,
abort it, reset to the remote's version, redo this run's changes to both
files on top of it (the user's edits win wherever they touch the same lines),
commit, and push once more. If that fails too, push nothing and say so in the
summary: the labels are already applied, and the next run starts from the
older `Last run:` line and finds these threads again.

**What sift writes outside the rubric reports, so it names the user.** Every
line sift writes in the state file and the commit message (reasons, the
summary, Observed and Daily review lines) and every changelog entry names the
user or says "you", even when it restates a rubric rule written as "I":
"nothing asked of Pat", not "nothing asked of me"; "not on Pat's Valued
list", not "not on my Valued list". None of them holds an account, card,
order, or ID number, or any part of one, including one in a subject: copy the
subject with the number left out ("Your receipt for order #4412" becomes
"Your receipt for order").

## Step 8: Summarize

Before writing the summary, go through this checklist. It is not optional: for
each item this run has not done, do it now, then continue.

- Step 3's four checks all pass now: no expired `(inferred)` line, no two
  About me headings for one subject, no note under the wrong heading, and the
  rubric within its size limits.
- Every sender whose lookup found something has an `(inferred)` note, and no
  sender About me already covered was looked up.
- Every action the Permissions section grants was carried out.
- On a run that created the files, the summary names the repository and
  folder that hold them.

Write the run summary at the top of the commit message's body (Step 7), then
repeat it in chat:

- The account this run sifted.
- Counts: processed, important, low priority, bulk, junk, starred, and moved
  to each tab, taken from what was actually applied this run.
- The important and starred threads, one line each with the reason.
- The daily review's line, when it ran, and the rubric changes it produced.
- Calls written into the rubric as `(inferred)` lines (see
  [Never block](#never-block)).
- Actions taken under a Permissions grant, such as threads archived.
- Anything skipped (a missing connector, a repository that failed the checks
  in Step 1, a push that didn't land).
- On a run that created the files, their repository and folder first.

Keep it scannable. The user should be able to read it in under a minute. A
scheduled run's chat output may have no reader, which is why the commit
carries it too. For the same reason, end on the summary, never on an offer or a
question. When the request asked for an action the rubric does not grant,
such as archiving, say it was not done and that the grant belongs in the
rubric's Permissions section. Do not offer to do it, or
to add the grant yourself: Permissions is the user's to write. Beyond the
commit and this reply, send no push notification or message about a run, whatever
tools exist, except one per thread the rubric's Notify section describes,
naming its sender and subject. A missing or empty Notify means none.

## Never block

When a run needs the user's judgment, it does not wait for it:

1. Take the safe default. For an unclear new thread, apply the rubric's When
   torn section (Step 6). For evidence too thin or mixed to settle a rule,
   change nothing.
2. When the rubric left a thread's call open and no line already covers that
   kind of mail, write the call into the rubric as a rule, in the section for
   the priority applied, so the user sees it there and the next run makes the
   same call: `(inferred) <the kind of mail, in the user's voice>: <priority> | <why it was a close call> | <run's date>`.
   Name the narrowest kind that covers it, as for any rule (Step 4), and note
   it in the changelog. The user corrects it by editing the line.
3. List each such line in the run summary.

Sift asks the user nothing during a run (the one exception is Step 1, when
the files can't be found and the user is there to answer), and the rubric's
text is the only place the user corrects sift.

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
needs (connectors, the repositories it clones, and the schedule), see
`references/running-as-a-routine.md`.
