#!/usr/bin/env python3
"""Measure a finished Notes section for the Step 8 summary rule.

Counts the words and lines of the text under `###### Notes` (up to the next
`######` label or `####` closing line): notes, captions, and quotes count;
images, blank lines, and Markdown syntax (bullets, emphasis markers, link
URLs) do not. Also counts topic sections, written as a paragraph holding
only bold text (`**Topic**`).

Prints JSON with the counts, which summary trigger fires, and the summary
length band the rule sets. The thresholds are the rule's approximate ones
(~500 words or ~40 lines; 3 or more sections); a count right at a threshold
is the model's call.

Standard library only (Python 3.9+).

The file must sit under the current folder, the home folder, or a temporary
folder.

Usage:
  measure_notes.py NOTES.md
  measure_notes.py -   (read the Markdown from standard input)
"""

import json
import os
import re
import sys
import tempfile

IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
# A link is its bracketed text followed at once by a destination: `(url)`,
# `(<url>)`, or either with a "title".
LINK_TEXT = re.compile(r"\[((?:[^\[\]]|\[[^\]]*\])+)\]")
DESTINATION = re.compile(r"\((?:<[^>]+>|[^)\s]+)(?:[ \t]+\"[^\"]*\")?\)")
TOPIC = re.compile(r"^\*\*[^*]+\*\*$|^__[^_]+__$")


def notes_section(lines):
    inside, section = False, []
    for line in lines:
        label = line.strip()
        if re.match(r"^######\s+Notes\s*$", label, re.IGNORECASE):
            inside = True
            continue
        if inside and (label.startswith("######") or re.match(r"^####\s", label)):
            break
        if inside:
            section.append(line)
    return section, inside


def link_text(text):
    """text with each Markdown link replaced by its link text."""
    out, pos = [], 0
    match = LINK_TEXT.search(text, pos)
    while match:
        dest = DESTINATION.match(text, match.end())
        if dest:
            out.append(text[pos:match.start()] + match.group(1))
            pos = dest.end()
            match = LINK_TEXT.search(text, pos)
        else:
            match = LINK_TEXT.search(text, match.start() + 1)
    return "".join(out) + text[pos:]


def plain(line):
    text = IMAGE.sub("", line.strip())
    text = link_text(text)
    text = re.sub(r"^>\s?", "", text)
    text = re.sub(r"^([-*+]|\d+[.)])\s+(\[[ xX]\]\s+)?", "", text)
    text = re.sub(r"[*_~`]+", "", text)
    return text.strip()


def measure(markdown):
    section, found = notes_section(markdown.replace("\r\n", "\n").split("\n"))
    words = lines = topics = 0
    for line in section:
        if TOPIC.match(line.strip()):
            topics += 1
        text = plain(line)
        if text:
            lines += 1
            words += len(text.split())
    long_notes = words > 500 or lines > 40
    sectioned = topics >= 3
    if words > 1000 or lines > 80:
        band = "up to five sentences, or one short bullet per topic section"
    elif long_notes:
        band = "two to three sentences"
    elif sectioned:
        band = "one to two sentences"
    else:
        band = None
    return {
        "notes_section_found": found,
        "words": words,
        "lines": lines,
        "topic_sections": topics,
        "triggers": {"length": long_notes, "three_or_more_sections": sectioned},
        "summary": "add" if long_notes or sectioned else "none",
        "summary_length": band,
    }


def safe_path(path):
    """path resolved, or exit when it is not Markdown or text under the
    current folder, the home folder, or a temporary folder (including the
    agent's scratch folder, CLAUDE_CODE_TMPDIR)."""
    resolved = os.path.realpath(path)
    if not resolved.lower().endswith((".md", ".markdown", ".txt")):
        sys.exit(f"measure_notes: {path} must be a .md, .markdown, or .txt file")
    roots = {os.getcwd(), os.path.expanduser("~"), tempfile.gettempdir(), "/tmp"}
    roots.update(os.environ[name] for name in ("TMPDIR", "TMP", "TEMP", "CLAUDE_CODE_TMPDIR")
                 if os.environ.get(name))
    for root in (os.path.realpath(r) for r in roots):
        if resolved.startswith(root.rstrip(os.sep) + os.sep):
            return resolved
    sys.exit(f"measure_notes: {path} is outside the current, home, and temporary folders")


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    if sys.argv[1] == "-":
        markdown = sys.stdin.read()
    else:
        with open(safe_path(sys.argv[1]), encoding="utf-8") as handle:
            markdown = handle.read()
    print(json.dumps(measure(markdown), indent=2))


if __name__ == "__main__":
    main()
