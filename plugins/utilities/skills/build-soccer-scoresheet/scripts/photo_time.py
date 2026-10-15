#!/usr/bin/env python3
"""Print each photo's capture time from its EXIF data.

Usage: python3 photo_time.py PHOTO [PHOTO ...]

Prints one JSON object per photo: the path, DateTimeOriginal as written by
the camera (local time), OffsetTimeOriginal (the UTC offset, when the camera
recorded one), and an ISO 8601 timestamp combining the two. Standard library
only, so it runs wherever Python 3 does. Reads JPEG files; for HEIC or PNG
files, or when a field is missing, the output says so and the caller should
fall back to another tool (exiftool, mdls) or another time source.
"""

import json
import struct
import sys

EXIF_IFD_POINTER = 0x8769
DATE_TIME_ORIGINAL = 0x9003
OFFSET_TIME_ORIGINAL = 0x9011
ASCII = 2


def read_exif_segment(data):
    """Return the TIFF payload of a JPEG's APP1 Exif segment, or None."""
    if data[:2] != b"\xff\xd8":
        return None
    position = 2
    while position + 4 <= len(data):
        if data[position] != 0xFF:
            return None
        marker = data[position + 1]
        length = struct.unpack(">H", data[position + 2:position + 4])[0]
        segment = data[position + 4:position + 2 + length]
        if marker == 0xE1 and segment[:6] == b"Exif\x00\x00":
            return segment[6:]
        if marker == 0xDA:  # start of scan: no more metadata segments
            return None
        position += 2 + length
    return None


def read_ifd(tiff, offset, endian):
    """Return {tag: (type, count, value_or_offset_bytes)} for one IFD."""
    entries = {}
    count = struct.unpack(endian + "H", tiff[offset:offset + 2])[0]
    for index in range(count):
        start = offset + 2 + index * 12
        tag, kind, number = struct.unpack(endian + "HHI", tiff[start:start + 8])
        entries[tag] = (kind, number, tiff[start + 8:start + 12])
    return entries


def ascii_value(tiff, entry, endian):
    kind, number, raw = entry
    if kind != ASCII:
        return None
    if number <= 4:
        value = raw[:number]
    else:
        offset = struct.unpack(endian + "I", raw)[0]
        value = tiff[offset:offset + number]
    return value.split(b"\x00", 1)[0].decode("ascii", "replace").strip() or None


def capture_time(path):
    result = {"path": path, "date_time_original": None,
              "offset_time_original": None, "iso": None}
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as error:
        result["error"] = str(error)
        return result
    tiff = read_exif_segment(data)
    if tiff is None:
        result["error"] = "no JPEG EXIF segment"
        return result
    endian = "<" if tiff[:2] == b"II" else ">"
    ifd0 = read_ifd(tiff, struct.unpack(endian + "I", tiff[4:8])[0], endian)
    if EXIF_IFD_POINTER not in ifd0:
        result["error"] = "no EXIF sub-IFD"
        return result
    exif_offset = struct.unpack(endian + "I", ifd0[EXIF_IFD_POINTER][2])[0]
    exif = read_ifd(tiff, exif_offset, endian)
    if DATE_TIME_ORIGINAL in exif:
        result["date_time_original"] = ascii_value(tiff, exif[DATE_TIME_ORIGINAL], endian)
    if OFFSET_TIME_ORIGINAL in exif:
        result["offset_time_original"] = ascii_value(tiff, exif[OFFSET_TIME_ORIGINAL], endian)
    local = result["date_time_original"]
    if local and len(local) >= 19:
        iso = local[:10].replace(":", "-") + "T" + local[11:19]
        result["iso"] = iso + (result["offset_time_original"] or "")
    return result


def main(paths):
    if not paths:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    for path in paths:
        print(json.dumps(capture_time(path), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
