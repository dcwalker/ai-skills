---
name: transcribe-apple-notes-to-dayone
description: Turn handwritten Apple Notes into Day One journal entries, each holding the handwriting as a PNG and a corrected plain-text transcription, dated with the note's creation date, then move each note into a done folder. Works in reviewed batches on macOS with the dayone CLI. Use when the user wants to import, transcribe, OCR, or move handwritten (Apple Pencil or drawing) notes from Apple Notes into Day One, and when they want to correct the text of a Day One entry that was imported from a handwritten note: the text of an entry with an image cannot be edited in place through the CLI.
metadata:
  category: utilities
---

# Transcribe Apple Notes to Day One

Import handwritten notes from an Apple Notes folder into a Day One journal.
Each note becomes one entry containing:

- the transcribed text, one line per handwritten line, corrected for
  recognition errors and misspellings
- the note's drawing as a PNG attachment, below the text
- the note's creation date and time as the entry date

After an entry is verified in Day One, the note moves to a done folder in
Notes. Notes are never edited or deleted.

## Requirements

- macOS with Notes, `osascript`, `python3`, and `swift` (Xcode Command Line
  Tools). Text recognition uses Apple's Vision framework, so nothing is sent
  to an outside OCR service.
- The `dayone` CLI, signed in (`dayone auth whoami` succeeds). If it is
  missing, stop and point the user to its setup; do not install it unasked.
  The Day One Mac app ships an older, unrelated `dayone` that can come first
  on `PATH`. If `which -a dayone` lists a path that resolves into
  `Day One.app/Contents/MacOS/` first, follow the `dayone-cli` skill's
  legacy-CLI preflight before running anything else.
- The first `dayone sync` on an account must have finished. Reads come from
  the CLI's local copy, which is incomplete until then.

The bundled scripts live in `scripts/`, resolved relative to this `SKILL.md`.
Do not hard-code an absolute install path: it contains a version identifier
that changes on every plugin update. Keep working files (extracted images,
transcriptions, results) in a directory created with `mktemp -d`, never in a
repository; the scripts write only under `$HOME` or `$TMPDIR`.

| Script | Purpose |
|--------|---------|
| `scripts/notes.py folders` | List every Notes account and folder with its note count |
| `scripts/notes.py scan` | List a folder's notes, newest first, with image count and typed-text length, never note text |
| `scripts/notes.py extract` | Save a note's inline images; reports size and duplicate copies |
| `scripts/notes.py move` | Move a note to a folder, creating the folder if needed |
| `scripts/pdf_image.py` | Pull the full-resolution drawing out of a PDF the user exported from Notes |
| `scripts/ocr.swift` | Recognize handwriting; slices tall images at blank rows |
| `scripts/dayone_entry.py write` | Create an entry with line breaks preserved and images attached |
| `scripts/dayone_entry.py verify` | Confirm entries landed: date, image count, line breaks, sync queue |

## Step 1: Settle the settings

Check before asking, so any question names real options:

1. Run `dayone auth whoami`. If it fails, stop: tell the user to sign in
   (`dayone auth login` or `dayone setup`) themselves, and ask nothing else.
2. Run `dayone list journals` and
   `python3 scripts/notes.py folders`, which lists every Notes account and
   folder with its note count.

Then settle five settings. Three have no default; ask for any the user has
not given or that the checks contradict, and do nothing else until they
answer:

1. **Source**: Notes account and folder. "My iCloud Notes folder" means
   account `iCloud`, folder `Notes`; a name that matches a listed folder is
   settled. Ask only when the request names no folder, or names one that
   does not exist, listing the real folders.
2. **Destination**: a Day One journal from `dayone list journals`, matched by
   name; use its numeric id from then on. If the named journal does not
   exist, list the journals and ask which to use; never create one or pick
   one yourself.
3. **Done folder**: the Notes folder imported notes move to, in the same
   account (for example `Exported to Day One`). It is created if missing.

Two have defaults. Use them without asking, and state them in the first
report so the user can change them:

4. **Batch size**: 10, unless the user gives another. The user reviews each
   batch in Day One before the next one starts.
5. **Corrections**: fix recognition errors and misspellings, including
   likely-intended words and the official spelling of product names, and
   keep the user's wording otherwise, unless the user says otherwise.

This skill never deletes notes. If the request asks for notes to be deleted
(after import or otherwise), the first thing the reply says is that notes
are moved to a done folder, never deleted, and it asks the user to name that
folder or agree to one. Do not leave the delete request unanswered.

The CLI cannot add tags. If the user wants entries tagged, tell them now that
they will add tags in the Day One app after each batch.

## Step 2: Find the handwritten notes

Run `dayone sync`, then:

```bash
python3 scripts/notes.py scan --account "<account>" --folder "<folder>"
```

Candidates are notes with `"handwritten": true`: at least one drawing and no
typed text beyond the title. Work newest first. Report the count and the date
range, and list notes with both a drawing and typed text separately; ask
before including them, and if included, put the typed text in the entry too.

Notes can hold passwords, codes, and personal details. Read only the notes
being imported, and never print or quote the text of other notes.

## Step 3: Prepare a batch

For each note in the batch, extract its images into its own directory:

```bash
python3 scripts/notes.py extract --id "<note id>" --out "<tmp>/<note>"
```

Check each image's size before going further:

- **Narrow images** (under about 1000 px wide while near the 3000 px height
  cap): Notes shrinks long drawings to fit, so the image is low resolution
  and recognition is poor. Hold the note, finish the rest of the batch, and
  ask the user to open it in Notes and choose File > Export as PDF, then give
  you the PDF's path. Extract the full-resolution drawing and use it in place
  of the inline image:

  ```bash
  python3 scripts/pdf_image.py "<exported.pdf>" "<tmp>/<note>/full.png"
  ```

  Rendering the PDF page instead scales the drawing back down; do not.
- **Duplicates**: `"copies": 2` means Notes stored the same drawing twice.
  Attach it once and mention it in the report.

## Step 4: Transcribe and correct

Recognize each image:

```bash
swift scripts/ocr.swift "<image>" "<tmp>/<note>"
```

Images taller than 2000 px are cut into slices at blank rows and recognized
slice by slice; the slices are saved next to the image.

Recognition output is a draft, not the transcription. Compare it against the
image (or each slice) yourself, line by line, and write the result to a text
file, one handwritten line per line:

- Fix recognition errors: wrong letters (`Sira` → `Jira`), digits read as
  letters (`L2` read as `12` or `42`), dropped or split lines, garbled
  symbols.
- Apply the corrections agreed in Step 1: misspellings, likely-intended words,
  and official product spellings.
- Keep the user's wording, line order, abbreviations, and capitalization
  where the handwriting is clear.
- Represent drawn arrows with text arrows (`→`, `↳`), and describe a sketch
  or chart in one bracketed line (`[Chart: ...]`) instead of transcribing it.
- When a reading stays uncertain, keep the closest reading and list it in the
  report for the user to check. Do not invent content.

## Step 5: Write, sync, verify

Write each entry with the note's `created` value from the scan as the date:

```bash
python3 scripts/dayone_entry.py write --journal-id <id> \
  --date "<created>" --text-file "<tmp>/<note>/final.txt" --image "<image>"
```

Then run `dayone sync`, and verify every entry written in the batch:

```bash
python3 scripts/dayone_entry.py verify --journal-id <id> \
  --entry-id <id1> --entry-id <id2> ...
```

An entry is good when its date matches the note, `images` equals the images
attached, `line_breaks` is one less than the transcription's count of
non-blank lines (`write` drops blank lines and escapes Markdown punctuation,
so the text shows exactly as transcribed), and
`outbox_pending` is 0 after the sync. In a shared journal that anyone can
edit, sync holds back an entry another person or device is editing and
reports the outbox as `deferred`; sync again once they are done rather than
clearing or retrying it. Investigate anything else before moving on.

## Step 6: Move the notes and report

Only after an entry verifies, move its note:

```bash
python3 scripts/notes.py move --id "<note id>" --account "<account>" --folder "<done folder>"
```

Report for the batch:

- how many entries were written and synced, with their date range
- notable corrections, and any uncertain readings to check against the image
- notes held for PDF export, and duplicate drawings attached once
- the tagging reminder, if the user tags entries
- how many handwritten notes remain

Then wait for the user before starting the next batch.

## Fixing an entry after it is written

### The date can be changed in place

`entry write` with `--entry-id` and `--date` changes an existing entry's
date, and the change reaches the server. On an entry that has an image the
rich text comes back unchanged, so the transcription and the attachment are
untouched. Use this whenever only the date is wrong; recreating the entry is
for text corrections.

A body is still required: `--date` on its own fails with `missing body;
provide --body or --body-stdin`. Send the stored body back with its Markdown
hard breaks intact, the way `entry_body` writes them, because a text-only
entry regenerates its rich text from the body and plain newlines collapse
into one paragraph. A body that already carries hard breaks can go back
verbatim.

Write the offset of the entry's own zone, not the machine's. Day One shows an
entry at its recorded zone, so an entry recorded three hours ahead of the
machine displays its header time only when `--date` carries that entry's
offset; send the machine's offset instead and it displays three hours late.
The CLI cannot show an entry's zone, so for any entry that is not in the
local zone, take the offset from an export or from what the user sees in the
app, and confirm the result the same way.

### The text cannot be changed in place

The CLI cannot change the text of an existing entry that has an image: it
keeps the old rich text and stores the new text only locally, with no error.
Re-attaching the image does not help either; it adds a second copy.

To correct the text, write a new entry with the fixed text and the same
image, verify it, then delete the old one with `dayone entry delete` and
sync. That needs the image file, which the CLI cannot retrieve: its store
keeps only a thumbnail and the moment's metadata. The image is still on disk
while the note's working files survive; after they are gone it has to come
from the note in Notes, or from a Day One export taken in the app, where each
exported photo is named by the `md5` its moment records and carries the width
and height recorded with it.

Deleting needs the user's confirmation first. When asking, say three
things: why a new entry was written instead of editing the old one (the CLI
cannot change the text of an entry that has an image), which entry will be
deleted, and that any tags added to it in the Day One app are lost with it.
The CLI's copy of an entry may not show tags added in the app, so do not tell
the user an entry has none.

## What a write does to an entry

After a write the CLI's own copy of the entry reports no time zone:
`time_zone` is null, and so is `timeZone` in its `data_json`. The entry keeps
its zone regardless; in one account's export, every entry written through
the CLI still carried one, including every entry this skill created. Never
read that null as data loss, and never use the CLI's view to work out what
time an entry displays.

A write can still move the zone to the writing machine's. In that same
export, 3 of 136 written entries had come back in the machine's zone rather
than their own, which is one sample and not a rate. Since the zone decides
the wall time Day One shows, a
date written for an entry recorded in another zone can display hours off the
time intended, and the CLI cannot show that it happened. For an entry whose
zone is not the local machine's, confirm the displayed time in the app or in
an export before calling it fixed. The Day One app's legacy `dayone`
binary (see Requirements) has `-z, --time-zone`, but its only command is
`new`, so it cannot set the zone of an entry that already exists.

A write replaces the whole body and carries no version with it, so the last
write wins. Several devices sync to one account, nothing is locked outside
shared journals (and there a lock only delays an upload), and the
local store is a cache that changes between reads: both entry ids and bodies
move. Re-read an entry in the same step that writes it, and compare its body,
date, and moment ids against what the plan was built from. Report an entry
that changed instead of overwriting it.

## Rules

- Never edit or delete a note in Notes; only move it, after its entry
  verifies.
- Never delete a Day One entry without the user's confirmation.
- Never overwrite an entry that changed since it was read; report it instead.
- Never run the import while a first-time `dayone sync` is still in progress.
- Never print or quote the content of notes outside the batch.
