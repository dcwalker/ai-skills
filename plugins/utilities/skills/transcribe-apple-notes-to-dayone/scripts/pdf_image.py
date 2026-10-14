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
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_paths import contained_path

NAMED_COMPONENTS = {b"DeviceRGB": 3, b"DeviceGray": 1}


def object_offsets(data):
    return {int(m.group(1)): m.start() for m in re.finditer(rb"(\d+) 0 obj", data)}


def object_body(data, objects, number):
    """The start of an indirect object's body, after its "N 0 obj" marker."""
    if number not in objects:
        sys.exit(f"the PDF refers to object {number}, which it does not contain")
    return objects[number] + len(f"{number} 0 obj")


def number_value(data, objects, header, key):
    """An integer entry such as /Width 1536 or /Length 12 0 R, or None if absent."""
    match = re.search(rb"/" + key + rb"\s+(\d+)(\s+\d+\s+R)?", header)
    if not match:
        return None
    if not match.group(2):
        return int(match.group(1))
    start = object_body(data, objects, int(match.group(1)))
    value = re.match(rb"\s*(\d+)", data[start : start + 40])
    if not value:
        sys.exit(f"could not read the /{key.decode()} value in the PDF")
    return int(value.group(1))


def read_stream(data, objects, start):
    header_end = data.find(b"stream", start)
    if header_end < 0:
        sys.exit("the PDF image has no data stream")
    body = header_end + len(b"stream")
    body += 2 if data[body : body + 2] == b"\r\n" else 1
    length = number_value(data, objects, data[start:header_end], b"Length")
    end = body + length if length is not None else data.find(b"endstream", body)
    try:
        return zlib.decompress(data[body:end])
    except zlib.error:
        sys.exit("could not decompress the PDF's image data")


def components(data, objects, header):
    """Color components per pixel: 1 (gray) or 3 (RGB)."""
    named = re.search(rb"/ColorSpace\s*/(\w+)", header)
    if named:
        if named.group(1) not in NAMED_COMPONENTS:
            sys.exit(f"unsupported color space {named.group(1).decode()}")
        return NAMED_COMPONENTS[named.group(1)]
    ref = re.search(rb"/ColorSpace\s+(\d+)\s+0\s+R", header)
    if not ref:
        sys.exit("the PDF image has no color space")
    start = object_body(data, objects, int(ref.group(1)))
    icc = re.search(rb"/ICCBased\s+(\d+)\s+0\s+R", data[start : start + 300])
    if not icc:
        sys.exit("unsupported color space; expected DeviceRGB, DeviceGray, or ICC")
    profile = object_body(data, objects, int(icc.group(1)))
    n = number_value(data, objects, data[profile : profile + 300], b"N")
    if n not in (1, 3):
        sys.exit(f"unsupported ICC color space with {n} components")
    return n


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


def largest_image(data, objects):
    """Return (offset, width, height, header) of the largest supported image."""
    best = None
    for match in re.finditer(rb"/Subtype\s*/Image", data):
        start = data.rfind(b"<<", 0, match.start())
        header = data[start : data.find(b"stream", start)]
        if b"/FlateDecode" not in header or b"/DecodeParms" in header:
            continue
        width = number_value(data, objects, header, b"Width")
        height = number_value(data, objects, header, b"Height")
        if not width or not height:
            continue
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


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    pdf_path = contained_path(sys.argv[1], "the PDF")
    png_path = contained_path(sys.argv[2], "the output PNG")
    with open(pdf_path, "rb") as f:
        data = f.read()
    objects = object_offsets(data)
    start, width, height, header = largest_image(data, objects)
    n = components(data, objects, header)
    pixels = read_stream(data, objects, start)
    if len(pixels) != width * height * n:
        sys.exit("unexpected image data size")
    mask = re.search(rb"/SMask\s+(\d+)\s+0\s+R", header)
    alpha = None
    if mask:
        alpha = read_stream(
            data, objects, object_body(data, objects, int(mask.group(1)))
        )
        if len(alpha) != width * height:
            sys.exit("unexpected alpha mask size")
    rows = [rgb_row(pixels, alpha, y * width, width, n) for y in range(height)]
    write_png(png_path, width, height, rows)
    print(json.dumps({"path": png_path, "width": width, "height": height}))


if __name__ == "__main__":
    main()
