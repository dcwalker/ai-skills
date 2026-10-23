# Organizing Apple Notes, and other apps

An example of applying the workflow to a system other than files. Mail, Reminders, and similar apps
follow the same pattern: learn what the app supports from its own documentation, decide whether item
names are labels or content, then plan only the operations it supports.

## What Notes supports

Notes' scripting dictionary (`sdef /System/Applications/Notes.app` on macOS) is the authoritative
reference. It shows:

- **Accounts** contain **folders**, and folders can contain folders, so nested structures work.
- A **note** has a read-only `id`, `creation date`, `modification date`, `plaintext`, and
  `container` (its folder), a writable `body` (HTML), and a writable `name`.
- The standard suite provides `make` (new folders) and `move` (a note to another folder). A moved
  note keeps its `id`.
- `password protected` and `shared` are reported per note, and `shared` per folder.

## What that means for the plan

- **A note's name is its first line.** Setting `name` rewrites the start of the note, so renaming a
  note edits its content. Propose renames separately from moves and apply them only with approval.
  Many users prefer to leave note titles alone and only file notes into folders.
- **Date notes only when the collection is a record**: meeting notes, journals, logs. A folder of
  recipes or reference lists gets categories, not dates.
- `creation date` is the fallback date for an undated note, but notes synced from another account or
  imported from elsewhere may carry the import date instead.
- Leave password-protected notes alone; their content can't be read to name them. Don't restructure
  shared folders without asking, since other people see the change.
- Verify moves by `id`: after the run, each note's `id` should be in its planned folder.
- Notes has no undo log of its own, so record each move (note `id`, old folder, new folder) in a
  durable file before making it.

## Other apps, briefly

- **Mail**: a message's subject is content. Organize by moving messages between mailboxes and by
  consolidating mailboxes; never rewrite subjects. Server-side rules may refile messages, so check
  for rules that would fight the new structure.
- **Reminders**: reminder text is content, and reminders are about future work, so no dates and no
  renaming. Organize the lists: consolidate near-duplicate lists, group lists by area, and move
  reminders between lists.
