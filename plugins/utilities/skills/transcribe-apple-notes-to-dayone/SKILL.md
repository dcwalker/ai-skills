---
name: transcribe-apple-notes-to-dayone
description: Turn handwritten Apple Notes into Day One journal entries, each holding the handwriting as a PNG and a corrected plain-text transcription, dated with the note's creation date, then move each note into a done folder. Works in reviewed batches on macOS with the dayone CLI. Use when the user wants to import, transcribe, OCR, or move handwritten (Apple Pencil or drawing) notes from Apple Notes into Day One.
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
- The first `dayone sync` on an account must have finished. Reads come from
  the CLI's local copy, which is incomplete until then.

The bundled scripts live in `scripts/`, resolved relative to this `SKILL.md`.
Do not hard-code an absolute install path: it contains a version identifier
that changes on every plugin update. Keep working files (extracted images,
transcriptions, results) in a directory created with `mktemp -d`, never in a
repository; the scripts write only under `$HOME` or `$TMPDIR`.

| Script | Purpose |
|--------|---------|
| `scripts/notes.py scan` | List a folder's notes, newest first, with image count and typed-text length, never note text |
| `scripts/notes.py extract` | Save a note's inline images; reports size and duplicate copies |
| `scripts/notes.py move` | Move a note to a folder, creating the folder if needed |
| `scripts/pdf_image.py` | Pull the full-resolution drawing out of a PDF the user exported from Notes |
| `scripts/ocr.swift` | Recognize handwriting; slices tall images at blank rows |
| `scripts/dayone_entry.py write` | Create an entry with line breaks preserved and images attached |
| `scripts/dayone_entry.py verify` | Confirm entries landed: date, image count, line breaks, sync queue |

## Step 1: Confirm the settings

Ask for anything the user has not given. Do not guess these:

1. **Source**: Notes account (often `iCloud`) and folder.
2. **Destination**: Day One journal. Run `dayone list journals` and confirm
   the journal by name; use its numeric id from then on.
3. **Done folder**: the Notes folder imported notes move to, in the same
   account (for example `Exported to Day One`). It is created if missing.
4. **Batch size**: default 10. The user reviews each batch in Day One before
   the next one starts.
5. **Corrections**: by default, fix recognition errors and misspellings,
   including likely-intended words and the official spelling of product
   names, and keep the user's wording otherwise. Confirm this or the user's
   preference.

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
`outbox_pending` is 0 after the sync. Investigate anything else before
moving on.

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

The CLI cannot change the text of an existing entry that has an image: it
keeps the old rich text and stores the new text only locally, with no error.
Re-attaching the image does not help either; it adds a second copy.

To correct an entry, write a new entry with the fixed text and the same
image, verify it, then delete the old one with `dayone entry delete` and
sync. Deleting needs the user's confirmation first, and tags added in the app
are lost with the old entry, so say so when asking.

## Rules

- Never edit or delete a note in Notes; only move it, after its entry
  verifies.
- Never delete a Day One entry without the user's confirmation.
- Never run the import while a first-time `dayone sync` is still in progress.
- Never print or quote the content of notes outside the batch.
