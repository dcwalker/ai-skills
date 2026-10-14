#!/usr/bin/env python3
"""Extract the full-resolution drawing from a PDF exported by Apple Notes.

Usage: pdf_image.py <in.pdf> <out.png>

Notes shrinks a long drawing to fit the note's width when it renders its
inline image, but File > Export as PDF embeds the drawing at full resolution
as a single Flate-encoded image. This writes the largest such image to a PNG,
composited onto white when it has an alpha mask, and prints its size as JSON.
Rendering the PDF page instead would scale the drawing down to letter size.

Both paths must lie under the user's home directory or $TMPDIR (where
mktemp creates files).
"""

import json
import os
import re
import struct
import sys
import tempfile
import zlib


def read_stream(data, start):
    header_end = data.find(b"stream", start)
    length = int(re.search(rb"/Length (\d+)", data[start:header_end]).group(1))
    body = header_end + len(b"stream")
    body += 2 if data[body : body + 2] == b"\r\n" else 1
    return zlib.decompress(data[body : body + length])


def object_offsets(data):
    return {int(m.group(1)): m.start() for m in re.finditer(rb"(\d+) 0 obj", data)}


def components(data, objects, header):
    named = re.search(rb"/ColorSpace /(\w+)", header)
    if named:
        return {b"DeviceRGB": 3, b"DeviceGray": 1}[named.group(1)]
    ref = int(re.search(rb"/ColorSpace (\d+) 0 R", header).group(1))
    space = data[objects[ref] : objects[ref] + 300]
    icc = re.search(rb"/ICCBased (\d+) 0 R", space)
    if not icc:
        sys.exit("unsupported color space")
    return int(
        re.search(rb"/N (\d+)", data[objects[int(icc.group(1))] :][:300]).group(1)
    )


def write_png(path, width, height, rgb_rows):
    def chunk(kind, body):
        return (
            struct.pack(">I", len(body))
            + kind
            + body
            + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
        )

    raw = b"".join(b"\x00" + row for row in rgb_rows)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        f.write(chunk(b"IEND", b""))


def largest_image(data):
    """Return (offset, width, height, header) of the largest supported image."""
    best = None
    for match in re.finditer(rb"/Subtype\s*/Image", data):
        start = data.rfind(b"<<", 0, match.start())
        header = data[start : data.find(b"stream", start)]
        if b"/FlateDecode" not in header or b"/DecodeParms" in header:
            continue
        width = int(re.search(rb"/Width (\d+)", header).group(1))
        height = int(re.search(rb"/Height (\d+)", header).group(1))
        if best is None or width * height > best[1] * best[2]:
            best = (start, width, height, header)
    if best is None:
        sys.exit("no supported embedded image found")
    return best


def rgb_row(pixels, alpha, first_pixel, width, n):
    """One row as RGB bytes, composited onto white when there is an alpha mask."""
    row = pixels[first_pixel * n : (first_pixel + width) * n]
    if n == 1:
        row = bytes(v for v in row for _ in range(3))
    if alpha is None:
        return row
    a = alpha[first_pixel : first_pixel + width]
    return bytes(255 - ((255 - row[i]) * a[i // 3]) // 255 for i in range(len(row)))


def allowed_roots():
    """Where this script may read or write: the user's home and $TMPDIR."""
    roots = {os.path.expanduser("~"), tempfile.gettempdir()}
    return sorted({os.path.realpath(root) for root in roots if os.path.isdir(root)})


def contained_path(path, name):
    """Resolve path, refusing anything outside the allowed roots."""
    resolved = os.path.realpath(os.path.expanduser(path))
    for root in allowed_roots():
        if resolved == root or resolved.startswith(root + os.sep):
            return resolved
    sys.exit(
        f"{name} must be inside your home directory or {tempfile.gettempdir()}; "
        f"got {path!r}. Create working folders with mktemp -d."
    )


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    pdf_path = contained_path(sys.argv[1], "the PDF")
    png_path = contained_path(sys.argv[2], "the output PNG")
    with open(pdf_path, "rb") as f:
        data = f.read()
    objects = object_offsets(data)
    start, width, height, header = largest_image(data)
    n = components(data, objects, header)
    pixels = read_stream(data, start)
    if len(pixels) != width * height * n:
        sys.exit("unexpected image data size")
    mask = re.search(rb"/SMask (\d+) 0 R", header)
    alpha = read_stream(data, objects[int(mask.group(1))]) if mask else None
    rows = [rgb_row(pixels, alpha, y * width, width, n) for y in range(height)]
    write_png(png_path, width, height, rows)
    print(json.dumps({"path": png_path, "width": width, "height": height}))


if __name__ == "__main__":
    main()
