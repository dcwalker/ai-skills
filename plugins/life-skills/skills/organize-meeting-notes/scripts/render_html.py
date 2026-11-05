#!/usr/bin/env python3
"""Render a finished meeting-notes Markdown file as a self-contained HTML page.

The page carries the skill's stylesheet (assets/meeting-notes.css) in a <style>
element, unchanged, opens with the palette picker the stylesheet styles, and
holds no script. Light or dark mode follows the browser.

It reads the Markdown subset the skill writes: ATX headings, paragraphs (a
single newline inside one becomes <br>, so attendee names keep their own
lines), bulleted and numbered lists nested by indentation, task items
(`- [ ]` and `- [x]`), blockquotes, images, links (including `(<url>)`), bold,
italics, strikethrough, and inline code. Anything else is kept as text,
escaped, so nothing is dropped.

Element mapping (what the stylesheet targets; follow it when building a page
by hand where this script cannot run):
  ## title                  <h2>, the metadata line right after it a <p>
  *italic-only paragraph*   <p><em>...</em></p> (schedule note, summary, caption)
  ###### label              <h6> (Attendees, Agenda, Notes, Action Items)
  attendee lines            one <p>, names separated by <br>, ~~name~~ as <del>
  **Topic** paragraph       <p><strong>Topic</strong></p>, then its <ul>
  > pull quote              <blockquote><p>...</p></blockquote> in the note's <li>
  nested bullets            a <ul> inside the <li> (chat exchanges)
  ![alt](path)              <p><img src alt></p>, its caption a <p><em>
  - [ ] / - [x] item        <li><input type="checkbox" disabled[ checked]> ...</li>
  #### closing line         <h4>
The page opens with <div class="page-controls"> holding the palette-switcher
fieldset (five radio inputs, Harbor checked), sets no data-theme or
data-palette on <html>, and copies the stylesheet unchanged into <style>.

An image whose file sits in the HTML file's folder or below keeps a relative
path. A local image anywhere else is embedded as a data: URI, so the page
still shows it after it is moved. Remote images keep their URL.

Standard library only (Python 3.9+).

Usage:
  render_html.py NOTES.md [--out NOTES.html] [--base DIR]

The output defaults to the Markdown path with an .html extension. --base is
the folder image paths are relative to (default: the Markdown file's
folder), for a Markdown file kept in a scratch directory. It prints the path
written.
"""

import argparse
import base64
import html
import mimetypes
import os
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_PATH = os.path.join(SKILL_DIR, "assets", "meeting-notes.css")

PALETTES = ("harbor", "evergreen", "plum", "ember", "teal")

LIST_ITEM = re.compile(r"^([-*+]|\d+[.)])[ \t]+")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$")
TASK = re.compile(r"^\[([ xX])\][ \t]+")
IMAGE_ONLY = re.compile(r"^!\[[^\]]*\]\([^)]*\)$")

# Inline patterns, tried at each position in this order.
INLINE = [
    ("code", re.compile(r"`([^`]+)`")),
    ("image", re.compile(r"!\[([^\]]*)\]\((?:<([^>]+)>|([^)\s]+))(?:[ \t]+\"([^\"]*)\")?\)")),
    ("link", re.compile(r"\[((?:[^\[\]]|\[[^\]]*\])+)\]\((?:<([^>]+)>|([^)\s]+))(?:[ \t]+\"([^\"]*)\")?\)")),
    ("bold", re.compile(r"\*\*(.+?)\*\*|__(.+?)__")),
    ("strike", re.compile(r"~~(.+?)~~")),
    ("italic", re.compile(r"(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])"
                          r"|(?<![\w_])_(?![\s_])(.+?)(?<![\s_])_(?![\w_])")),
]


class Renderer:
    def __init__(self, md_dir, out_dir):
        self.md_dir = md_dir
        self.out_dir = out_dir
        self.warnings = []

    # ---------- Inline ----------

    def inline(self, text):
        out, pos = [], 0
        while pos < len(text):
            best = None
            for kind, pattern in INLINE:
                match = pattern.search(text, pos)
                if match and (best is None or match.start() < best[1].start()):
                    best = (kind, match)
            if best is None:
                break
            kind, match = best
            out.append(html.escape(text[pos:match.start()], quote=False))
            out.append(self.inline_element(kind, match))
            pos = match.end()
        out.append(html.escape(text[pos:], quote=False))
        return "".join(out)

    def inline_element(self, kind, match):
        if kind == "code":
            return "<code>" + html.escape(match.group(1), quote=False) + "</code>"
        if kind == "image":
            src = match.group(2) or match.group(3)
            return self.image(match.group(1), src, match.group(4))
        if kind == "link":
            href = html.escape(match.group(2) or match.group(3), quote=True)
            title = match.group(4)
            title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
            return f'<a href="{href}"{title_attr}>{self.inline(match.group(1))}</a>'
        inner = next(g for g in match.groups() if g is not None)
        tag = {"bold": "strong", "strike": "del", "italic": "em"}[kind]
        return f"<{tag}>{self.inline(inner)}</{tag}>"

    def image(self, alt, src, title):
        alt_attr = html.escape(alt, quote=True)
        title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
        return f'<img src="{html.escape(self.image_src(src), quote=True)}" alt="{alt_attr}"{title_attr}>'

    def image_src(self, src):
        if re.match(r"^[a-z][a-z0-9+.-]*:", src, re.IGNORECASE):
            return src  # http(s):, data:, and other URLs stay as written
        path = os.path.realpath(os.path.join(self.md_dir, os.path.expanduser(src)))
        out_dir = os.path.realpath(self.out_dir)
        if os.path.commonpath([path, out_dir]) == out_dir:
            return os.path.relpath(path, out_dir).replace(os.sep, "/")
        if not os.path.isfile(path):
            self.warnings.append(f"image not found, kept as written: {src}")
            return src
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as handle:
            data = base64.b64encode(handle.read()).decode("ascii")
        return f"data:{mime};base64,{data}"

    # ---------- Blocks ----------

    def blocks(self, lines):
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue
            heading = HEADING.match(stripped)
            if heading and line == line.lstrip():
                level = len(heading.group(1))
                out.append(f"<h{level}>{self.inline(heading.group(2))}</h{level}>")
                i += 1
                continue
            if re.match(r"^(\*\s*){3,}$|^(-\s*){3,}$|^(_\s*){3,}$", stripped):
                out.append("<hr>")
                i += 1
                continue
            if stripped.startswith(">"):
                quote = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote.append(re.sub(r"^\s*>[ \t]?", "", lines[i]))
                    i += 1
                out.append("<blockquote>\n" + "\n".join(self.blocks(quote)) + "\n</blockquote>")
                continue
            if LIST_ITEM.match(line):
                html_list, i = self.list_block(lines, i)
                out.append(html_list)
                continue
            if IMAGE_ONLY.match(stripped):
                # An image gets its own paragraph, so a caption under it
                # stays a paragraph of its own.
                out.append("<p>" + self.inline(stripped) + "</p>")
                i += 1
                continue
            para = []
            while i < len(lines):
                current = lines[i]
                if not current.strip() or para and (
                        LIST_ITEM.match(current) or current.strip().startswith(">")
                        or HEADING.match(current.strip()) or IMAGE_ONLY.match(current.strip())):
                    break
                para.append(current.strip())
                i += 1
            out.append("<p>" + "<br>\n".join(self.inline(p) for p in para) + "</p>")
        return out

    def list_block(self, lines, i):
        ordered = LIST_ITEM.match(lines[i]).group(1)[0].isdigit()
        indent = len(lines[i]) - len(lines[i].lstrip())
        items = []
        while i < len(lines):
            line = lines[i]
            match = LIST_ITEM.match(line.lstrip())
            line_indent = len(line) - len(line.lstrip())
            if not match or line_indent != indent or match.group(1)[0].isdigit() != ordered:
                break
            content_col = line_indent + match.end()
            body = [line.lstrip()[match.end():]]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    # A blank line ends the item unless indented content follows.
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and len(lines[j]) - len(lines[j].lstrip()) > indent:
                        body.append("")
                        i += 1
                        continue
                    break
                nxt_indent = len(nxt) - len(nxt.lstrip())
                if nxt_indent <= indent:
                    break
                body.append(nxt[min(nxt_indent, content_col):] if nxt_indent >= content_col
                            else nxt.lstrip())
                i += 1
            items.append(self.list_item(body))
        tag = "ol" if ordered else "ul"
        return f"<{tag}>\n" + "\n".join(items) + f"\n</{tag}>", i

    def list_item(self, body):
        first, rest = body[0], body[1:]
        checkbox = ""
        task = TASK.match(first)
        if task:
            checked = " checked" if task.group(1).lower() == "x" else ""
            checkbox = f'<input type="checkbox" disabled{checked}> '
            first = first[task.end():]
        # Lines that continue the first paragraph (not a new block) join it.
        lead = [first]
        while rest and rest[0].strip() and not (
                LIST_ITEM.match(rest[0]) or rest[0].strip().startswith(">")
                or IMAGE_ONLY.match(rest[0].strip())):
            lead.append(rest.pop(0).strip())
        text = "<br>\n".join(self.inline(part) for part in lead)
        children = self.blocks(rest)
        if children:
            return f"<li>{checkbox}{text}\n" + "\n".join(children) + "\n</li>"
        return f"<li>{checkbox}{text}</li>"


def plain_title(markdown_lines):
    for line in markdown_lines:
        match = re.match(r"^##[ \t]+(.+)$", line)
        if match:
            return re.sub(r"[*_~`\[\]]|\]\([^)]*\)", "", match.group(1)).strip()
    return "Meeting notes"


def palette_switcher():
    rows = []
    for name in PALETTES:
        checked = " checked" if name == "harbor" else ""
        rows.append(f'    <label><input type="radio" name="palette" value="{name}"{checked}> '
                    f'{name.capitalize()}</label>')
    return ('<div class="page-controls">\n  <fieldset class="palette-switcher">\n'
            "    <legend>Color</legend>\n" + "\n".join(rows) + "\n  </fieldset>\n</div>")


def render(md_path, out_path, base=None):
    with open(md_path, encoding="utf-8") as handle:
        lines = handle.read().replace("\r\n", "\n").split("\n")
    with open(CSS_PATH, encoding="utf-8") as handle:
        css = handle.read()
    renderer = Renderer(os.path.abspath(base) if base else os.path.dirname(os.path.abspath(md_path)),
                        os.path.dirname(os.path.abspath(out_path)))
    body = "\n".join(renderer.blocks(lines))
    page = (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{html.escape(plain_title(lines), quote=False)}</title>\n"
        f"<style>\n{css}</style>\n</head>\n<body>\n{palette_switcher()}\n\n{body}\n</body>\n</html>\n"
    )
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(page)
    return renderer.warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("markdown", help="the finished meeting notes (.md)")
    parser.add_argument("--out", help="the HTML file to write (default: beside the Markdown)")
    parser.add_argument("--base", help="the folder image paths are relative to (default: the Markdown's)")
    args = parser.parse_args()
    if not os.path.isfile(args.markdown):
        sys.exit(f"render_html: no such file: {args.markdown}")
    out = args.out or os.path.splitext(args.markdown)[0] + ".html"
    if not out.lower().endswith(".html"):
        sys.exit("render_html: --out must end in .html")
    if args.base and not os.path.isdir(args.base):
        sys.exit(f"render_html: no such folder: {args.base}")
    for warning in render(args.markdown, out, args.base):
        print(f"render_html: warning: {warning}", file=sys.stderr)
    print(os.path.abspath(out))


if __name__ == "__main__":
    main()
