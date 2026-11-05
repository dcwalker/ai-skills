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
path. A local image file anywhere else under the allowed folders (below) is
embedded as a data: URI, so the page still shows it after it is moved; any
other local file keeps its path as written, unread. Remote images keep their
URL. Links may be relative or use http, https, or mailto, and images http,
https, or a data:image/ URI; any other scheme (javascript:, file:) leaves
the text without a link or image, with a warning.

Standard library only (Python 3.9+).

Usage:
  render_html.py NOTES.md [--out NOTES.html] [--base DIR]

The output defaults to the Markdown path with an .html extension. --base is
the folder image paths are relative to (default: the Markdown file's
folder), for a Markdown file kept in a scratch directory. It prints the path
written. Both files must sit under the current folder, the home folder, or a
temporary folder the environment names (TMPDIR, TMP, TEMP, or
CLAUDE_CODE_TMPDIR).
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

HTML_SUFFIX = ".html"
TEMP_VARIABLES = ("TMPDIR", "TMP", "TEMP", "CLAUDE_CODE_TMPDIR")

PALETTES = ("harbor", "evergreen", "plum", "ember", "teal")

LIST_ITEM = re.compile(r"^([-*+]|\d+[.)])[ \t]+")
TASK = re.compile(r"^\[([ xX])\][ \t]+")
IMAGE_ONLY = re.compile(r"^!\[[^\]]*\]\([^)]*\)$")
RULE = re.compile(r"^(\*\s*){3,}$|^(-\s*){3,}$|^(_\s*){3,}$")
BLANKS = " \t"


def heading(text):
    """An ATX heading's level and text, or None. Trailing #s are dropped."""
    level = len(text) - len(text.lstrip("#"))
    rest = text[level:]
    if not 1 <= level <= 6 or rest[:1] not in (" ", "\t") or not rest:
        return None
    return level, rest.strip(BLANKS).rstrip("#").rstrip(BLANKS)


class InlineMatch:
    """The parts of a link or image match that inline_element reads."""

    def __init__(self, start, end, groups):
        self._start, self._end, self._groups = start, end, groups

    def start(self):
        return self._start

    def end(self):
        return self._end

    def group(self, index):
        return self._groups[index - 1]

    def groups(self):
        return self._groups


# A link or image is its bracketed text, matched here, followed at once by
# a destination, matched by DESTINATION: `(url)`, `(<url>)`, or either with
# a "title".
LINK_TEXT = re.compile(r"\[((?:[^\[\]]|\[[^\]]*\])+)\]")
IMAGE_TEXT = re.compile(r"!\[([^\]]*)\]")
DESTINATION = re.compile(r"\((?:<([^>]+)>|([^)\s]+))(?:[ \t]+\"([^\"]*)\")?\)")


class BracketPattern:
    """search() like a compiled pattern, for bracketed text plus destination."""

    def __init__(self, text_pattern):
        self.text_pattern = text_pattern

    def search(self, text, pos):
        match = self.text_pattern.search(text, pos)
        while match:
            dest = DESTINATION.match(text, match.end())
            if dest:
                return InlineMatch(match.start(), dest.end(), (match.group(1),) + dest.groups())
            match = self.text_pattern.search(text, match.start() + 1)
        return None


# Inline patterns, tried at each position in this order.
INLINE = [
    ("code", re.compile(r"`([^`]+)`")),
    ("image", BracketPattern(IMAGE_TEXT)),
    ("link", BracketPattern(LINK_TEXT)),
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
            target = match.group(2) or match.group(3)
            if not safe_link(target):
                self.warnings.append(f"link scheme not allowed, kept as text: {target}")
                return self.inline(match.group(1))
            href = html.escape(target, quote=True)
            title = match.group(4)
            title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
            return f'<a href="{href}"{title_attr}>{self.inline(match.group(1))}</a>'
        inner = next(g for g in match.groups() if g is not None)
        tag = {"bold": "strong", "strike": "del", "italic": "em"}[kind]
        return f"<{tag}>{self.inline(inner)}</{tag}>"

    def image(self, alt, src, title):
        if not safe_image_url(src):
            self.warnings.append(f"image scheme not allowed, kept as text: {src}")
            return html.escape(alt, quote=False)
        alt_attr = html.escape(alt, quote=True)
        title_attr = f' title="{html.escape(title, quote=True)}"' if title else ""
        return f'<img src="{html.escape(self.image_src(src), quote=True)}" alt="{alt_attr}"{title_attr}>'

    def image_src(self, src):
        if url_scheme(src):
            return src  # http(s): and data:image/ URLs stay as written
        path = os.path.realpath(os.path.join(self.md_dir, os.path.expanduser(src)))
        out_dir = os.path.realpath(self.out_dir)
        if os.path.commonpath([path, out_dir]) == out_dir:
            return os.path.relpath(path, out_dir).replace(os.sep, "/")
        if not os.path.isfile(path):
            self.warnings.append(f"image not found, kept as written: {src}")
            return src
        # Embed only an image file from an allowed folder, so a path in the
        # notes cannot copy another file's contents into a shared page.
        mime = mimetypes.guess_type(path)[0] or ""
        if not mime.startswith("image/") or not within_roots(path):
            self.warnings.append(f"not an image in an allowed folder, kept as written: {src}")
            return src
        with open(path, "rb") as handle:
            data = base64.b64encode(handle.read()).decode("ascii")
        return f"data:{mime};base64,{data}"

    # ---------- Blocks ----------

    def blocks(self, lines):
        out, i = [], 0
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue
            html_block, i = self.block(lines, i)
            out.append(html_block)
        return out

    def block(self, lines, i):
        """The block that starts at a non-blank line i, and the line after it."""
        line = lines[i]
        stripped = line.strip()
        title = heading(stripped)
        if title and line == line.lstrip():
            level, text = title
            return f"<h{level}>{self.inline(text)}</h{level}>", i + 1
        if RULE.match(stripped):
            return "<hr>", i + 1
        if stripped.startswith(">"):
            return self.blockquote(lines, i)
        if LIST_ITEM.match(line):
            return self.list_block(lines, i)
        if IMAGE_ONLY.match(stripped):
            # An image gets its own paragraph, so a caption under it stays a
            # paragraph of its own.
            return "<p>" + self.inline(stripped) + "</p>", i + 1
        return self.paragraph(lines, i)

    def blockquote(self, lines, i):
        quote = []
        while i < len(lines) and lines[i].strip().startswith(">"):
            quote.append(re.sub(r"^\s*>[ \t]?", "", lines[i]))
            i += 1
        return "<blockquote>\n" + "\n".join(self.blocks(quote)) + "\n</blockquote>", i

    def paragraph(self, lines, i):
        para = []
        while i < len(lines) and not ends_paragraph(lines[i], bool(para)):
            para.append(lines[i].strip())
            i += 1
        return "<p>" + "<br>\n".join(self.inline(p) for p in para) + "</p>", i

    def list_block(self, lines, i):
        ordered = LIST_ITEM.match(lines[i]).group(1)[0].isdigit()
        indent = indent_of(lines[i])
        items = []
        while i < len(lines):
            line = lines[i]
            match = LIST_ITEM.match(line.lstrip())
            if not match or indent_of(line) != indent or match.group(1)[0].isdigit() != ordered:
                break
            body, i = item_body(lines, i, indent, indent + match.end())
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


LINK_SCHEMES = ("http", "https", "mailto")
IMAGE_SCHEMES = ("http", "https")


def url_scheme(target):
    """A URL's scheme in lowercase, or "" for a relative path or #anchor."""
    match = re.match(r"([a-z][a-z0-9+.-]*):", target.strip(), re.IGNORECASE)
    return match.group(1).lower() if match else ""


def safe_link(target):
    """A relative link, or one using http, https, or mailto."""
    scheme = url_scheme(target)
    return not scheme or scheme in LINK_SCHEMES


def safe_image_url(src):
    """A relative path, an http(s) URL, or a data: URI holding an image."""
    scheme = url_scheme(src)
    if scheme == "data":
        return src.strip().lower().startswith("data:image/")
    return not scheme or scheme in IMAGE_SCHEMES


def indent_of(line):
    return len(line) - len(line.lstrip())


def ends_paragraph(line, started):
    """Whether line ends a paragraph: a blank line, or once the paragraph has
    a line, the start of another block."""
    stripped = line.strip()
    if not stripped:
        return True
    return started and bool(LIST_ITEM.match(line) or stripped.startswith(">")
                            or heading(stripped) or IMAGE_ONLY.match(stripped))


def blank_continues(lines, i, indent):
    """Whether the blank line i sits inside a list item: indented content
    follows the blank lines."""
    j = i + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    return j < len(lines) and indent_of(lines[j]) > indent


def item_body(lines, i, indent, content_col):
    """A list item's lines with its marker and indentation removed, and the
    line after the item."""
    body = [lines[i].lstrip()[content_col - indent:]]
    i += 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            if not blank_continues(lines, i, indent):
                break
            body.append("")
        elif indent_of(line) <= indent:
            break
        else:
            body.append(line[content_col:] if indent_of(line) >= content_col else line.lstrip())
        i += 1
    return body, i


def plain_title(markdown_lines):
    for line in markdown_lines:
        rest = line[2:] if line.startswith("##") else ""
        if rest[:1] in (" ", "\t") and len(rest) > 1:
            # The title starts after the blanks, keeping at least one character.
            title = rest.lstrip(BLANKS) or rest[-1]
            return re.sub(r"[*_~`\[\]]|\]\([^)]*\)", "", title).strip()
    return "Meeting notes"


def palette_switcher():
    rows = []
    for name in PALETTES:
        checked = " checked" if name == "harbor" else ""
        rows.append(f'    <label><input type="radio" name="palette" value="{name}"{checked}> '
                    f'{name.capitalize()}</label>')
    return ('<div class="page-controls">\n  <fieldset class="palette-switcher">\n'
            "    <legend>Color</legend>\n" + "\n".join(rows) + "\n  </fieldset>\n</div>")


def allowed_roots():
    """The folders this script reads notes and images from and writes pages
    to: the current folder, the home folder, and the temporary folders the
    environment names, including the agent's scratch folder
    (CLAUDE_CODE_TMPDIR)."""
    roots = {os.getcwd(), os.path.expanduser("~")}
    roots.update(os.environ[name] for name in TEMP_VARIABLES if os.environ.get(name))
    return [os.path.realpath(root) for root in roots]


def within_roots(resolved):
    return any(resolved.startswith(root.rstrip(os.sep) + os.sep) for root in allowed_roots())


def safe_path(path, suffixes):
    """path resolved, or exit when it falls outside allowed_roots() or does not
    end in one of suffixes, so a wrong argument cannot reach another file."""
    resolved = os.path.realpath(path)
    if not resolved.lower().endswith(suffixes):
        sys.exit(f"render_html: {path} must end in {' or '.join(suffixes)}")
    if not within_roots(resolved):
        sys.exit(f"render_html: {path} is outside the current, home, and temporary folders")
    return resolved


def render(md_path, out_path, base=None):
    md_path = safe_path(md_path, (".md", ".markdown", ".txt"))
    out_path = safe_path(out_path, (HTML_SUFFIX,))
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
    out = args.out or os.path.splitext(args.markdown)[0] + HTML_SUFFIX
    if not out.lower().endswith(HTML_SUFFIX):
        sys.exit(f"render_html: --out must end in {HTML_SUFFIX}")
    if args.base and not os.path.isdir(args.base):
        sys.exit(f"render_html: no such folder: {args.base}")
    for warning in render(args.markdown, out, args.base):
        print(f"render_html: warning: {warning}", file=sys.stderr)
    print(os.path.abspath(out))


if __name__ == "__main__":
    main()
