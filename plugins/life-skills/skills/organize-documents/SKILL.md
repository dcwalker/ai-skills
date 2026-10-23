---
name: organize-documents
description: >
  Organize a collection of documents or items into a consistent naming scheme and container structure,
  reading each item's content to date, categorize, and describe it, then applying an approved plan
  without overwriting or deleting anything. Works on any system that holds items in containers: files
  in folders, notes in Apple Notes folders, messages in email folders, reminders in lists. Use whenever
  the user wants to organize, sort, file, rename, clean up, or restructure a folder, archive, or
  collection of many items, such as "organize my scanned documents", "rename these PDFs", "clean up
  my Notes folders", "sort my receipts into folders", or "consolidate my Reminders lists", even if
  they don't name a format. Not for deciding the next action on each item of a backlog (use triage),
  and not for cleaning up the text of one set of meeting notes (use organize-meeting-notes).
metadata:
  category: life-skills
---

# Organize Documents

Turn a disorganized collection into one where every item has a predictable name and lives in a
predictable place. The work is mostly reading: an item's name and location come from what it is, so
each item's content has to be understood before it can be named. The rest is care: the collection
belongs to the user, often holds records they can't replace, and the plan is theirs to approve.

## Naming scheme

For collections where history matters, items are named:

```
YYYY-MM-DD - Category - Description
```

- **Date** is the date of the document itself: the statement date, invoice date, letter date,
  meeting date, or signature date. Use the most specific date the content supports, and drop
  precision only when the content does: when the day can't be determined use `YYYY-MM`, and when the
  month can't be determined use `YYYY`.
  - Documents that cover a period are dated by that period when it's printed: a tax form by its tax
    year (`2018 - Woodgrove Brokerage - Form 1099-DIV`), a statement by its closing date.
  - Resolve an ambiguous numeric date such as `07/02/2019` from context (currency, address,
    language, other dates in the document) and state the assumption in the plan. Ask only when
    nothing in the content settles it.
  - The item's creation date in the system is the last resort, used when the content offers no
    date and no indirect clue. Use it even if it looks recent, and say in the plan that it is the
    creation date, so the user can correct it.
  - Never use a modification date: sync tools, backups, and downloads rewrite file dates on disk,
    so they describe the copy, not the document. A scanner's timestamp in a filename
    (`20240105093012.pdf`) is when the page was scanned, not when it was written.
- **Category** is where the item came from or what it belongs to: a company, a project, a recurring
  meeting series, or a person. Which kind fits depends on the collection; an archive of household
  paperwork groups by issuing company, a work folder by project, a notes folder by meeting series.
- **Description** says what the item is, from its content: `Receipt`, `Invoice 60103`,
  `Explanation of Benefits`, `Offer Letter`, `Quarterly Planning Notes`. Add a person's name in
  parentheses when the item concerns one specific person in a shared collection, such as
  `Statement (Alex)`. Keep identifiers short and never include full account, card, or government ID
  numbers in a name.

Separate the parts with ` - ` (space, hyphen, space) and keep characters that are illegal or awkward
in names on that system (`/`, `:`) out of every part.

### When dates belong in the name

Dates earn their place when the collection is a record of things that happened and chronological
order matters: tax documents, statements, receipts, correspondence, medical records, meeting notes.
They don't belong in collections focused on future work or timeless reference: reminder lists, to-do
lists, project task lists, recipes, manuals. For those, the structure is categories alone, and item
names are `Category - Description` or left as they are.

Decide which kind of collection this is during the survey. Strong signals for dating: the items carry
their own dates, they record events or transactions, the user will look for them by when they
happened. If the signals are mixed, ask.

### When items get renamed at all

Rename an item only when its name is a label rather than part of its content:

- **Files**: the filename is a label. Rename freely within the approved plan.
- **Notes** whose title is their first line: renaming rewrites the note. Propose it, explain that
  the first line will change, and rename only with approval.
- **Email messages, reminders, tasks, and similar**: the subject or text is the content. Never
  rewrite it. These items are organized by moving them between containers, not by renaming.

When it's unclear whether a system's item names are labels or content, ask before planning renames.

## Container structure

Containers are whatever the system groups items in: folders, mailboxes, lists, notebooks.

- **An existing pattern wins.** If the collection is already organized by category, by year, by
  year then category, or anything else consistent, follow it, even if you'd have chosen differently.
- **Otherwise organize by category**, or by category then description when a category holds many
  items of a few recurring kinds (`Woodgrove Bank/Statements/`, `Woodgrove Bank/Tax Forms/`).
- **Consolidate near-duplicate containers** (`Woodgrove Bnak` and `Woodgrove Bank`, `Contoso` and
  `Contoso Ltd`) into one canonical name.
- **Resolve competing containers by the dominant pattern.** When two containers hold the same kind of
  content under different schemes, such as a person folder (`Alex/`) and a company folder
  (`Proseware Pediatrics/`) that both hold that clinic's records, the problem is the duplicate
  structure, not just where one new item goes. Review the rest of the collection to see which
  scheme is established (most folders named by company, or by person), then merge the outlier's
  items into the dominant structure, renamed to match (add `(Alex)` when moving a person's records
  into a company folder), and file the new item there too. Follow a different scheme only if the
  user chose it earlier. Ask only when neither scheme clearly dominates.

## Workflow

### 1. Survey without changing anything

Inventory the collection: how many items, what kinds, how they're named today, and what containers
exist. Note how many items already follow the scheme, how many are partly named, and how many have
meaningless names such as scanner timestamps or `Document 1`.

Check what the system can do, because the plan can only include operations it supports:

- Can items be renamed, and would that change their content?
- Can containers be created, renamed, and merged?
- Can items be moved between containers, and does a move preserve the item (its identity, its
  history, its attachments)?

Find this out from the system's own documentation or tool descriptions rather than by trying
operations on the user's data. Then read the reference for the system, if there is one:

- Files and folders: [references/files.md](references/files.md)
- Apple Notes: [references/apple-notes.md](references/apple-notes.md), which also shows the
  pattern for other apps such as Mail and Reminders

### 2. Learn the conventions already in use

Before inventing anything, study the items that are already organized. Collect the category names in
use, how descriptions are worded, how people are referenced, and how containers are laid out. New
names should be indistinguishable from the existing well-named ones: reuse an existing category's
exact spelling for the same organization, and match the existing description style.

Complete names that are partly there (`2016-02-11 - City Power & Light`) from the content. Where
patterns compete, the most common one is the established one; see Container structure above.

### 3. Read every item that needs work

Determine the date, category, and description from content, not from the current name. Extract the
text layer, use OCR for scans, and look at the page directly for handwriting, photos, and anything
where extracted text is too thin to understand. An existing name is a useful hint, but verify it.

Record a confidence for each item (high, medium, low) and a short reason for anything below high,
such as "date inferred from billing period" or "handwritten, no date". For undated items, look for
indirect clues in the content before falling back to the creation date: a form revision date, a
model year, a child's stated grade, a referenced event.

For large collections, split the items into batches and work through them in parallel if you can
delegate work. Give every batch the same written conventions so the results agree, then reconcile
category spellings across batches before building the plan.

### 4. Show the plan, then apply it

Users would rather have the work done with a way to undo it than supervise each step, so the default
is to show the plan and carry it out in the same turn. The safeguards in step 5 are what make that
safe: every change is a reversible rename or move, and the undo log reverses the whole run.

The plan lists:

- Every change: current name and location, new name and location, confidence, reason. For a large
  plan, write it to a file (CSV or TSV) the user can open and summarize the counts in the
  conversation.
- Container changes: new containers, merges, and containers the run leaves empty.
- Collisions: two items that would get the same name. Make the names unique with a detail from the
  content that tells them apart, such as an invoice number, account, or person
  (`... - Invoice 8812`, `... - Statement (Sam)`). Fall back to a number (`... Receipt 2`) only
  when the content offers nothing distinguishing. Never overwrite, and don't ask the user to choose
  names.
- Byte-identical duplicates (confirmed with a byte comparison, not just a matching name or size):
  keep the copy with the best name and location, and move the others to the Trash (step 5).

Stop after showing the plan, without applying it, only when:

- The user asked for a proposal only ("just propose names", "don't change anything yet").
- A category or pattern is genuinely ambiguous and the existing data doesn't settle it.
- A step would rewrite item content (such as renaming notes), move anything outside the collection,
  or permanently delete anything.

Apply everything else and list any open questions in the report, with a recommended answer for
each. If the user changes rules partway through, apply them to the whole plan, not just the
remaining items.

### 5. Apply the plan safely

The collection may hold the only copy of important records, so every change must be reversible:

- **Rename and move only.** Never permanently delete an item, even when asked. Duplicates and
  anything the user wants removed go to the system Trash, where the user decides whether to empty
  it. If the Trash can't be used (no permission, or the system has none), create a folder named
  `Trash` at the top of the collection and move them there for the user to review.
- **Never overwrite.** Use an operation that refuses to replace an existing item, and check again
  immediately before each change.
- **Stay inside the collection.** Nothing moves outside the root the user named unless they ask.
- **Keep an undo log** of every change (old location, new location) somewhere durable. Unless the
  user has a preferred place, use `~/organize-documents-logs/<collection name>/<YYYY-MM-DD-HHMM>/`,
  with the plan and the move log side by side, so every run's logs are in one predictable place.
  Temporary directories get cleared by the operating system within days, which would leave the user
  with no way back.
- **Run a preflight first.** Confirm every source still exists and no destination is taken before
  the first change, so a problem stops the run before it starts rather than halfway through.

### 6. Verify and report

Confirm the item count is unchanged and every item arrived where the plan said. Where the system
allows it, confirm each item is the same item (a file's inode and size, or its checksum; a note's
ID). Remove containers the run left empty, and record each removal in the undo log.

Then report plainly: what changed, what was skipped and why, which items are low confidence and worth
a look, and where the undo log is with the command to reverse the run. State the integrity checks
outright, such as "nothing was overwritten or deleted; every file kept its inode and size", because
for an archive of records that is the first thing the user needs to know.

## Asking the user

Settle what the data can settle, and ask only when:

- A category isn't clear from the content, and the existing data has no precedent for it.
- Competing patterns are evenly matched, so neither is established.
- It's unclear whether item names are labels or content, or whether dates belong in the scheme.
- A step would permanently delete anything, move anything outside the collection, or rewrite item
  content.

Don't ask about things the content already answers, such as a date format the currency makes clear.
Batch questions, and offer a recommended answer first for each so the user can approve quickly.
