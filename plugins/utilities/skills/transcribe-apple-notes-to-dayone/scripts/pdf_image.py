#!/usr/bin/env python3
"""Extract the full-resolution drawing from a PDF exported by Apple Notes.

Usage: pdf_image.py <in.pdf> <out.png>

Notes shrinks a long drawing to fit the note's width when it renders its
inline image, but File > Export as PDF embeds the drawing at full resolution
as a single Flate-encoded image. This writes the largest such image to a PNG,
composited onto white when it has an alpha mask, and prints its size as JSON.
Rendering the PDF page instead would scale the drawing down to letter size.
"""

import json
import re
import struct
import sys
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


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    objects = object_offsets(data)
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
    start, width, height, header = best
    n = components(data, objects, header)
    pixels = read_stream(data, start)
    if len(pixels) != width * height * n:
        sys.exit("unexpected image data size")
    mask = re.search(rb"/SMask (\d+) 0 R", header)
    alpha = read_stream(data, objects[int(mask.group(1))]) if mask else None
    rows = []
    for y in range(height):
        row = pixels[y * width * n : (y + 1) * width * n]
        if n == 1:
            row = bytes(v for v in row for _ in range(3))
        if alpha is not None:
            a = alpha[y * width : (y + 1) * width]
            row = bytes(
                255 - ((255 - row[i]) * a[i // 3]) // 255 for i in range(len(row))
            )
        rows.append(row)
    write_png(sys.argv[2], width, height, rows)
    print(json.dumps({"path": sys.argv[2], "width": width, "height": height}))


if __name__ == "__main__":
    main()
