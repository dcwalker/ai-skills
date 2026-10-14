#!/usr/bin/env python3
"""Write and verify Day One entries for transcribe-apple-notes-to-dayone.

Subcommands:
  write   Create one entry from a plain-text file plus image attachments.
  verify  Report what Day One stored for entries, to confirm a write landed.

The dayone CLI turns an entry body into Day One's rich text by parsing it as
Markdown, which joins plain newlines into one paragraph, turns lines like
"1. Item" or "- item" into lists, and reads characters like * and _ as
formatting. write keeps the handwritten text literal: each line is trimmed,
blank lines are dropped, Markdown punctuation is backslash-escaped, and every
line but the last ends with a Markdown hard break (a trailing backslash).
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime

# ASCII punctuation Markdown can read as formatting, links, HTML, or entities
# anywhere in a line. Escaping it keeps the character literal.
INLINE_SPECIAL = re.compile(r"([\\`*_\[\]<>~|!&=])")
# What else can change a line's meaning when it comes first: headings,
# quotes, list bullets, setext underlines (--- or ===), and numbered lists.
LINE_START_SPECIAL = re.compile(r"^([#>+\-])|^(\d+)([.)])")


def escape_line(line):
    line = INLINE_SPECIAL.sub(r"\\\1", line.strip())
    return LINE_START_SPECIAL.sub(
        lambda m: f"\\{m.group(1)}" if m.group(1) else f"{m.group(2)}\\{m.group(3)}",
        line,
        count=1,
    )


def entry_body(text, image_count):
    lines = [escape_line(line) for line in text.split("\n") if line.strip()]
    body = "\\\n".join(lines)
    placeholders = "\n\n".join("![](dayone-moment://)" for _ in range(image_count))
    return body + ("\n\n" + placeholders if placeholders else "")


def dayone(args, stdin=None):
    result = subprocess.run(
        ["dayone", *args], input=stdin, capture_output=True, text=True, check=False
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.exit(result.stderr.strip() or result.stdout.strip() or "dayone failed")


def write(args):
    with open(args.text_file) as f:
        text = f.read()
    cmd = [
        "entry",
        "write",
        "--journal-id",
        args.journal_id,
        "--date",
        args.date,
        "--body-stdin",
    ]
    for image in args.image:
        cmd += ["--attach", image, "--attach-type", "image"]
    print(json.dumps(dayone(cmd, entry_body(text, len(args.image)))))


def summarize_entry(item):
    """What verify reports for one stored entry."""
    rich = item.get("richTextJSON") or "{}"
    contents = (json.loads(rich) if isinstance(rich, str) else rich).get("contents", [])
    texts = [node["text"] for node in contents if "text" in node]
    return {
        "date": datetime.fromtimestamp(item["date"] / 1000).astimezone().isoformat(),
        "images": len(item.get("moments") or []),
        "line_breaks": texts.count("\n"),
        "first_line": texts[0] if texts else "",
    }


def journal_pages(journal_id):
    """Yield each page of a journal's entries, following the CLI's cursor."""
    cmd = ["list", "entries", "--journal-id", journal_id, "--limit", "100"]
    cmd += ["--fields", "id,date,moments,richTextJSON"]
    cursor = None
    while True:
        page = dayone(cmd + (["--cursor", cursor] if cursor else []))
        yield page.get("items", [])
        cursor = page.get("next_cursor")
        if not cursor:
            return


def verify(args):
    wanted, found = set(args.entry_id), {}
    for items in journal_pages(args.journal_id):
        for item in items:
            if item["id"] in wanted:
                found[item["id"]] = summarize_entry(item)
        if not wanted - set(found):
            break
    outbox = dayone(["outbox", "list"]).get("items", [])
    print(
        json.dumps(
            {
                "entries": found,
                "missing": sorted(wanted - set(found)),
                "outbox_pending": len(outbox),
            },
            indent=1,
            ensure_ascii=False,
        )
    )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("write", help="create one entry")
    p.add_argument("--journal-id", required=True)
    p.add_argument(
        "--date",
        required=True,
        help="RFC 3339 date with UTC offset, e.g. 2026-02-05T11:45:01-08:00",
    )
    p.add_argument(
        "--text-file",
        required=True,
        help="the transcription, one handwritten line per line",
    )
    p.add_argument(
        "--image",
        action="append",
        default=[],
        help="image to attach; repeat for several",
    )
    p.set_defaults(func=write)
    p = sub.add_parser("verify", help="report stored entries and the sync queue")
    p.add_argument("--journal-id", required=True)
    p.add_argument(
        "--entry-id", action="append", required=True, help="repeat for several"
    )
    p.set_defaults(func=verify)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
