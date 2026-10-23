#!/usr/bin/env python3
"""Apply an approved rename/move plan to a directory tree, without overwriting or deleting.

The plan is a tab-separated file with a header row and columns `old_path` and `new_path`, both
relative to --root. Every row is checked before anything changes (preflight): the source exists,
the destination stays inside the root, no destination is already taken, and no two rows share a
destination (compared case-insensitively, since macOS and Windows filesystems usually are).

Each rename refuses to replace an existing item, atomically where the OS supports it
(renamex_np RENAME_EXCL on macOS, renameat2 RENAME_NOREPLACE on Linux). Each completed move is
appended to --log immediately, in the same format as the plan, so the log stays accurate even if
the run stops partway. Passing a log as --plan with --undo reverses it, last move first. Afterward every
moved item is checked to still have the same inode and size, which proves its bytes are untouched
without reading them (safe for cloud placeholder files).

Usage:
  apply_moves.py --root DIR --plan plan.tsv --log moves.log [--dry-run]
  apply_moves.py --root DIR --plan moves.log --undo --log undo.log [--dry-run]
"""

import argparse
import csv
import ctypes
import ctypes.util
import os
import sys


def no_clobber_rename(old, new):
    """Rename old to new, failing if new exists. Raises OSError on failure."""
    libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        result = libc.renamex_np(os.fsencode(old), os.fsencode(new), ctypes.c_uint(0x4))  # RENAME_EXCL
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        at_fdcwd = -100
        result = libc.renameat2(at_fdcwd, os.fsencode(old), at_fdcwd, os.fsencode(new), ctypes.c_uint(1))  # RENAME_NOREPLACE
    else:
        if os.path.lexists(new):
            raise FileExistsError(f"destination exists: {new}")
        os.rename(old, new)
        return
    if result != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno), new)


def is_case_only_change(old, new):
    return old != new and old.lower() == new.lower()


def load_plan(path, undo=False):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if not {"old_path", "new_path"} <= set(reader.fieldnames or []):
            sys.exit("plan must have a tab-separated header row with old_path and new_path columns")
        rows = []
        for line, r in enumerate(reader, start=2):
            if not r["old_path"] or not r["new_path"]:
                sys.exit(f"plan line {line} is missing old_path or new_path")
            rows.append((r["old_path"], r["new_path"]))
    if undo:
        rows = [(new, old) for old, new in reversed(rows)]
    return [(old, new) for old, new in rows if old != new]


def preflight(root, plan):
    errors, seen, checked = [], set(), []
    for old_rel, new_rel in plan:
        old, new = os.path.join(root, old_rel), os.path.normpath(os.path.join(root, new_rel))
        if not os.path.lexists(old):
            errors.append(f"source missing: {old_rel}")
            continue
        if not new.startswith(root + os.sep):
            errors.append(f"destination outside root: {new_rel}")
        if new.lower() in seen:
            errors.append(f"two rows share destination: {new_rel}")
        seen.add(new.lower())
        if os.path.lexists(new) and not is_case_only_change(old, new):
            errors.append(f"destination exists: {new_rel}")
        stat = os.lstat(old)
        checked.append((old, new, stat.st_ino, stat.st_size))
    return checked, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", required=True, help="collection root; nothing moves outside it")
    parser.add_argument("--plan", required=True, help="TSV with old_path and new_path columns")
    parser.add_argument("--log", required=True, help="durable log path (not a temp directory)")
    parser.add_argument("--undo", action="store_true", help="treat --plan as a log and reverse it")
    parser.add_argument("--dry-run", action="store_true", help="run the preflight only")
    args = parser.parse_args()

    root = os.path.realpath(args.root)
    moves, errors = preflight(root, load_plan(args.plan, args.undo))
    print(f"preflight: {len(moves)} moves, {len(errors)} problems")
    for e in errors:
        print("  " + e)
    if errors:
        sys.exit(1)
    if args.dry_run:
        return

    new_log = not os.path.exists(args.log)
    with open(args.log, "a", newline="", encoding="utf-8") as log:
        writer = csv.writer(log, delimiter="\t")
        if new_log:
            writer.writerow(["old_path", "new_path"])
        for done, (old, new, _, _) in enumerate(moves):
            os.makedirs(os.path.dirname(new), exist_ok=True)
            try:
                if is_case_only_change(old, new):
                    os.rename(old, new)  # same item on a case-insensitive filesystem
                else:
                    no_clobber_rename(old, new)
            except OSError as e:
                sys.exit(f"stopped after {done} moves at {os.path.relpath(old, root)}: {e}")
            writer.writerow([os.path.relpath(old, root), os.path.relpath(new, root)])
            log.flush()
            os.fsync(log.fileno())

    mismatched = [new for old, new, ino, size in moves
                  if not os.path.lexists(new) or os.lstat(new).st_ino != ino or os.lstat(new).st_size != size]
    remaining = [old for old, new, _, _ in moves if os.path.lexists(old) and not is_case_only_change(old, new)]
    print(f"moved {len(moves)}; inode or size mismatches: {len(mismatched)}; sources still present: {len(remaining)}")
    for path in mismatched:
        print("  mismatch: " + os.path.relpath(path, root))
    if mismatched or remaining:
        sys.exit(2)


if __name__ == "__main__":
    main()
