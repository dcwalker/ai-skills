#!/usr/bin/env python3
"""Read and move Apple Notes through AppleScript, for transcribe-apple-notes-to-dayone.

Subcommands:
  scan     List a folder's notes as JSON, newest first, with structure only
           (image count, typed-text length), never the note text itself.
  extract  Save a note's inline images to a directory and print their details.
  move     Move a note into a folder, creating the folder if it is missing.

Note IDs, account names, and folder names are passed to osascript as
arguments, never interpolated into script source, so names with quotes or
spaces are safe. macOS asks once for permission to control Notes.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
from datetime import datetime

SCAN_JS = r"""
function run(argv) {
  const [accountName, folderName] = argv;
  const Notes = Application('Notes');
  const account = Notes.accounts.byName(accountName);
  const folder = account.folders.byName(folderName);
  return JSON.stringify(folder.notes().map(n => {
    const body = n.body();
    const images = (body.match(/<img[^>]+src="data:image\//g) || []).length;
    const typed = body.replace(/<img[^>]*>/g, '').replace(/<[^>]+>/g, ' ')
                      .replace(/&nbsp;/g, ' ').trim();
    return {id: n.id(), name: n.name(), created: n.creationDate().toISOString(),
            images: images, typed_chars: typed.length};
  }));
}
"""

BODY_AS = """on run argv
  tell application "Notes" to return body of note id (item 1 of argv)
end run"""

MOVE_AS = """on run argv
  set {noteId, accountName, folderName} to argv
  tell application "Notes"
    set acc to account accountName
    if not (exists folder folderName of acc) then make new folder at acc with properties {name:folderName}
    move note id noteId to folder folderName of acc
  end tell
end run"""


def osascript(args, language=None):
    cmd = ["osascript"] + (["-l", language] if language else [])
    result = subprocess.run(cmd + args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        sys.exit(result.stderr.strip() or "osascript failed")
    return result.stdout


def png_size(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    return None, None


def scan(args):
    notes = json.loads(
        osascript(["-e", SCAN_JS, args.account, args.folder], "JavaScript")
    )
    for note in notes:
        created = datetime.fromisoformat(note["created"].replace("Z", "+00:00"))
        note["created"] = created.astimezone().isoformat()
        # Handwriting-only notes: at least one drawing and no typed text beyond the title.
        note["handwritten"] = note["images"] > 0 and note["typed_chars"] <= len(
            note["name"]
        )
    notes.sort(key=lambda n: n["created"], reverse=True)
    print(json.dumps(notes, indent=1, ensure_ascii=False))


def extract(args):
    body = osascript(["-e", BODY_AS, args.id])
    os.makedirs(args.out, exist_ok=True)
    images, seen = [], {}
    for index, (kind, encoded) in enumerate(
        re.findall(r'src="data:image/(\w+);base64,([^"]+)"', body)
    ):
        data = base64.b64decode(encoded)
        digest = hashlib.sha256(data).hexdigest()
        if digest in seen:
            # Notes sometimes stores the same drawing twice; attach it once.
            images[seen[digest]]["copies"] += 1
            continue
        path = os.path.join(args.out, f"img{index}.{kind}")
        with open(path, "wb") as f:
            f.write(data)
        width, height = png_size(data)
        seen[digest] = len(images)
        images.append({"path": path, "width": width, "height": height, "copies": 1})
    print(json.dumps({"id": args.id, "images": images}, indent=1))


def move(args):
    osascript(["-e", MOVE_AS, args.id, args.account, args.folder])
    print(json.dumps({"id": args.id, "moved_to": f"{args.account}/{args.folder}"}))


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("scan", help="list a folder's notes as JSON, newest first")
    p.add_argument("--account", required=True, help='Notes account name, e.g. "iCloud"')
    p.add_argument("--folder", required=True)
    p.set_defaults(func=scan)
    p = sub.add_parser("extract", help="save a note's inline images")
    p.add_argument("--id", required=True, help="note id from scan")
    p.add_argument("--out", required=True, help="directory to write images into")
    p.set_defaults(func=extract)
    p = sub.add_parser("move", help="move a note into a folder, creating it if needed")
    p.add_argument("--id", required=True)
    p.add_argument("--account", required=True)
    p.add_argument("--folder", required=True)
    p.set_defaults(func=move)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
