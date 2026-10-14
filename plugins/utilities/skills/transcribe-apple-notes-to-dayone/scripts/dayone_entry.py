#!/usr/bin/env python3
"""Write and verify Day One entries for transcribe-apple-notes-to-dayone.

Subcommands:
  write   Create one entry from a plain-text file plus image attachments.
  verify  Report what Day One stored for entries, to confirm a write landed.

The dayone CLI turns an entry body into Day One's rich text by parsing it as
Markdown, which joins plain newlines into one paragraph and turns lines like
"1. Item" or "- item" into lists. write keeps the handwritten layout by
ending each line with a Markdown hard break (a trailing backslash) and
escaping characters that would start a list, heading, or quote.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime

MARKDOWN_LINE_START = re.compile(r"^(\s*)(\d+)([.)])(\s)|^(\s*)([-+*#>])(\s|$)")


def escape_line(line):
    def repl(m):
        if m.group(2) is not None:
            return f"{m.group(1)}{m.group(2)}\\{m.group(3)}{m.group(4)}"
        return f"{m.group(5)}\\{m.group(6)}{m.group(7)}"

    return MARKDOWN_LINE_START.sub(repl, line, count=1)


def entry_body(text, image_count):
    lines = [escape_line(line.rstrip()) for line in text.strip().split("\n")]
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


def verify(args):
    wanted, found, cursor = set(args.entry_id), {}, None
    while wanted - set(found):
        cmd = [
            "list",
            "entries",
            "--journal-id",
            args.journal_id,
            "--limit",
            "100",
            "--fields",
            "id,date,moments,richTextJSON",
        ]
        page = dayone(cmd + (["--cursor", cursor] if cursor else []))
        for item in page.get("items", []):
            if item["id"] in wanted:
                rich = item.get("richTextJSON") or "{}"
                contents = (json.loads(rich) if isinstance(rich, str) else rich).get(
                    "contents", []
                )
                texts = [node["text"] for node in contents if "text" in node]
                found[item["id"]] = {
                    "date": datetime.fromtimestamp(item["date"] / 1000)
                    .astimezone()
                    .isoformat(),
                    "images": len(item.get("moments") or []),
                    "line_breaks": texts.count("\n"),
                    "first_line": texts[0] if texts else "",
                }
        cursor = page.get("next_cursor")
        if not cursor:
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
