# Organizing files and folders

Specifics for when the collection is files in a directory tree. The workflow and naming rules in
`SKILL.md` still apply; this covers what is particular to files.

## Survey

- Count files by extension and by naming state (already in the scheme, partly named, meaningless).
  Exclude system clutter such as `.DS_Store` and `Thumbs.db` from counts, and leave it in place.
- Treat package bundles as single items, never descending into them: macOS `.pages`, `.numbers`,
  `.key`, `.app`, `.photoslibrary`, and similar directories are one document each, and moving a
  file out of one corrupts it.
- **Cloud placeholders.** iCloud Drive (Optimize Mac Storage), OneDrive, Dropbox, and Google Drive
  can keep files online-only. On macOS, `find <root> -type f -flags +dataless` lists iCloud ones.
  Renames and moves are metadata-only and safe on placeholders, but reading content, including
  hashing, downloads each file. Expect reading many placeholders to be slow, and avoid reading
  content you don't need.

## Reading content

Choose the cheapest method that gives enough to name the file:

| Type | Method |
| --- | --- |
| PDF with a text layer | `pdftotext`, Python `pypdf`, or on macOS a small Swift script using PDFKit's `page.string` |
| Scanned PDF or image | OCR: `tesseract`, `ocrmypdf`, or on macOS the Vision framework (`VNRecognizeTextRequest`) without installing anything |
| Handwriting, photos, drawings | Look at the page image directly; OCR is unreliable here |
| `.doc`, `.docx`, `.rtf`, `.txt` | On macOS `textutil -convert txt -stdout <file>`; elsewhere `pandoc` or `python-docx` |
| `.pages`, `.numbers`, `.key` | The bundle or zip holds `QuickLook/Preview.pdf` or `preview.jpg`; read that |
| `.epub` | Unzip and read the OPF metadata (title, publisher) and the copyright page for the edition year |
| `.xlsx`, `.xls` | Unzip `xl/sharedStrings.xml` for `.xlsx`; for old binary `.xls` (check with `file`, even if the extension says `.xlsx`) use `strings` |

Reading the first two pages is usually enough to date and identify a document. Write extracted text
to a temporary working directory, never into the collection.

Check each file's type with `file` when its extension and behavior disagree; mislabeled files are
common in old archives. Keep the original extension when renaming unless the user asks otherwise.

## Dates

The file's creation date is the last resort for an undated document, and only creation, never
modification. Even creation dates are unreliable after a sync or restore, so when you do use one,
say so in the plan's reason column. Scanner filenames such as `20240105093012.pdf` or
`2019_03_08_14_22_40.pdf` record the scan time, not the document date.

## Applying the plan

- **Renames on the same volume are metadata-only**: the file's bytes never move, so content can't be
  damaged. Moves across volumes copy and delete, so keep everything on the collection's volume.
- **Use a no-clobber rename.** Plain `mv` and Python's `os.rename` silently replace an existing
  destination on POSIX systems. Use `mv -n`, or [scripts/apply_moves.py](../scripts/apply_moves.py),
  which refuses to overwrite atomically where the OS allows it.
- Filesystems are often case-insensitive (macOS and Windows by default), so `Receipt.pdf` and
  `receipt.pdf` collide. Compare destinations case-insensitively when checking for collisions.
- To find duplicates cheaply, group by size first and hash only files that share a size, then
  confirm with a byte comparison (`cmp`) before treating two files as identical.
- **Moving to the Trash**: on macOS 14 and later use `/usr/bin/trash <path>`; elsewhere `gio trash`
  (Linux desktops) or the platform's recycle bin. The Trash can refuse some items, such as cloud
  files the app doesn't own; when it does, fall back to a `Trash` folder at the top of the
  collection and say so in the report.
- Remove only directories that are truly empty, with `rmdir` (which refuses a non-empty one), never
  descending into package bundles, and add each removal to the undo log so the run can be reversed.

## Verifying

A rename keeps a file's inode, so an unchanged inode and size after the move proves the bytes are
untouched, without reading (or downloading) the content. For a full check, hash every file before
and after and confirm each checksum appears the same number of times.

## scripts/apply_moves.py

Applies a plan file with columns `old_path` and `new_path` (tab-separated, relative to the
collection root):

```bash
python3 scripts/apply_moves.py --root <collection> --plan plan.tsv --log <durable-dir>/moves.log --dry-run
python3 scripts/apply_moves.py --root <collection> --plan plan.tsv --log <durable-dir>/moves.log
```

The dry run checks every row: source exists, source and destination both resolve inside the root
(following symlinks), the destination is not taken, and no two rows share a destination. Without
`--dry-run` it applies the rows, writing each one to the log just before its rename and removing it
if the rename fails (so a stopped run never leaves a moved file without a log row), and verifies
inode and size afterward. To undo a run, pass its log as the plan with `--undo`, which reverses it
last move first and skips any row whose move never happened:

```bash
python3 scripts/apply_moves.py --root <collection> --plan <durable-dir>/moves.log --undo --log <durable-dir>/undo.log
```
