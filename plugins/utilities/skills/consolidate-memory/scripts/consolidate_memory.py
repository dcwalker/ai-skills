#!/usr/bin/env python3
"""Inventory, promote, and clean up Claude Code memory across projects, and check the shared tree.

Claude Code keeps one directory per project under <claude-dir>/projects/, named with a lossy
slug of the project path. Each holds session transcripts (*.jsonl, plus UUID-named artifact
directories) and, for some projects, auto memory in memory/ with a MEMORY.md index. The shared
tree (--tree) uses the same layout as Claude app memory: profile.md,
preferences.md, and topics/, areas/, and people/ directories of Markdown files.

Commands:
  inventory   Report every project directory, its real path, and whether that path still
              exists; every memory file with its frontmatter; index problems; near-duplicate
              memories across projects and the tree; and dead ~/.claude.json project entries.
  promote     Apply an approved promotion plan: copy a memory into the tree ("move") or confirm
              it was already merged into a tree file ("remove"), then take the project copy out
              of its memory directory and MEMORY.md, keeping a backup.
  cleanup     Remove transcripts of projects whose directory no longer exists, and remove dead
              project entries from ~/.claude.json.
  seed        Copy a Claude app memory export into the tree, never overwriting.
  check-tree  Check the tree's files for the layout, frontmatter, and size Claude app memory
              accepts.

Every command that changes files only reports what it would do unless passed --apply.

A project's real path comes from the cwd recorded in its transcripts, never from decoding the
directory name. A path counts as gone only when it is provably absent: a path that fails to stat
for another reason, is relative, or sits on a volume that is not mounted, is kept. Cleanup never
deletes a memory/ directory (it records the project's path beside it instead), backs up
~/.claude.json before rewriting it, refuses while another Claude session is running unless passed
--ignore-sessions, and refuses when nearly everything looks dead unless passed --force.

Usage:
  consolidate_memory.py inventory [--json]
  consolidate_memory.py promote --plan plan.json [--apply]
  consolidate_memory.py cleanup [--apply] [--ignore-sessions] [--force]
  consolidate_memory.py seed --from EXPORT_DIR [--apply]
  consolidate_memory.py check-tree [--json]

Common options: --claude-dir (default ~/.claude), --claude-json (default ~/.claude.json), and
--tree. The tree defaults to a memories folder in iCloud Drive (~/Library/Mobile
Documents/com~apple~CloudDocs/memories), so the Claude iOS and desktop apps can open it; without
iCloud Drive, ~/Documents/memories; without a Documents folder, ~/memories. Every path the
script writes under must be inside the home or temp directory.

A promotion plan is a JSON list of objects, each source appearing once. A "remove" target must
exist already or be created by an earlier "move" in the same plan:
  {"action": "move", "source": "<project memory file>", "target": "topics/name.md"}
  {"action": "remove", "source": "<project memory file>", "target": "preferences.md"}
"""

import argparse
import collections
import datetime
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

TREE_ROOT_FILES = ("profile.md", "preferences.md")
TREE_DIRS = ("topics", "areas", "people")
WEB_FILE_BYTE_CAP = 49152
INDEX_LINE_LIMIT = 200
INDEX_BYTE_LIMIT = 25 * 1024
DUPLICATE_THRESHOLD = 0.4
STOPWORDS = frozenset({
    "the", "and", "for", "with", "are", "this", "that", "from", "not", "never", "always", "should",
    "must", "when", "use", "user", "into", "than", "then", "them", "they", "their", "there",
    "what", "which", "who", "will", "would", "can", "could", "about", "after", "before", "only",
    "also", "each", "its", "just", "like", "more", "most", "other", "some", "such", "very", "was",
    "were", "been", "has", "have", "had", "our", "out", "over", "own", "same", "how", "why",
    "apply",
})
MASS_DELETION_SHARE = 0.9
MASS_DELETION_MINIMUM = 5
TRANSCRIPT_HEAD_LINES = 200
CLEANED_MARKER = ".consolidate-memory-project.json"
EMPTY = "<no conversation>"
CLAUDE_NAMES = ("claude", "claude-code")
SCRIPT_HOSTS = ("node", "bun")
VOLUME_PARENTS = ("/Volumes", "/Network", "/mnt", "/media", "/run/media")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
INDEX_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def input_path(path, option):
    """Resolve a read-only input path. Inputs aren't confined to home or temp: an export on another
    volume is fine to read."""
    if not isinstance(path, str) or not path:
        sys.exit(f"{option} must be a path")
    return os.path.realpath(os.path.expanduser(path))


def checked_arg_path(path, option):
    """Resolve a command-line path, exiting unless it is under the home or temp directory."""
    if not isinstance(path, str) or not path:
        sys.exit(f"{option} must be a path")
    resolved = os.path.realpath(os.path.expanduser(path))
    for base in (os.path.expanduser("~"), tempfile.gettempdir(), "/tmp", "/private/tmp"):
        base = os.path.realpath(base)
        if resolved == base or resolved.startswith(base + os.sep):
            return resolved
    sys.exit(f"{option} must be inside your home directory or the temp directory: {path}")


def default_tree():
    """The tree's default location: iCloud Drive when present, then Documents, then home."""
    home = os.path.expanduser("~")
    for parent in (os.path.join(home, "Library", "Mobile Documents", "com~apple~CloudDocs"),
                   os.path.join(home, "Documents")):
        if os.path.isdir(parent):
            return os.path.join(parent, "memories")
    return os.path.join(home, "memories")


def timestamp():
    return datetime.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")


# ---------- frontmatter and memory files ----------


def normalized(text):
    """Drop a UTF-8 byte order mark and convert CRLF line endings, so frontmatter parses the same
    whatever editor last saved the file."""
    return text.removeprefix("\ufeff").replace("\r\n", "\n")


def split_frontmatter(text):
    """Return (header, rest) for text that opens with a frontmatter block, else (None, text).
    rest starts at the closing --- line."""
    text = normalized(text)
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end:]


def parse_frontmatter(text):
    """Parse the YAML-subset frontmatter Claude memory files use: top-level keys, one level of
    nested keys (such as metadata.type), and folded or literal block values (description: >).
    Returns (fields, body)."""
    header, rest = split_frontmatter(text)
    if header is None:
        return {}, normalized(text)
    fields, parent, block_key = {}, None, None
    for line in header.splitlines():
        if block_key is not None:
            if line.startswith((" ", "\t")) or not line.strip():
                fields[block_key] = (fields[block_key] + " " + line.strip()).strip()
                continue
            block_key = None
        if not line.strip():
            continue
        match = re.match(r"^(\s*)([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not match:
            continue
        indent, key, value = match.groups()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if indent and parent is not None:
            fields[parent][key] = value
        elif value in (">", "|", ">-", "|-", ">+", "|+"):
            fields[key], parent, block_key = "", None, key
        elif value:
            fields[key], parent = value, None
        else:
            fields[key], parent = {}, key
    body = rest[4:].lstrip("\n")
    return fields, body


def memory_type(fields):
    metadata = fields.get("metadata")
    if isinstance(metadata, dict) and metadata.get("type"):
        return metadata["type"]
    value = fields.get("type")
    return value if isinstance(value, str) else None


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def describe_memory(path):
    text = read_text(path)
    fields, body = parse_frontmatter(text)
    name = fields.get("name") if isinstance(fields.get("name"), str) else None
    description = fields.get("description") if isinstance(fields.get("description"), str) else None
    return {
        "path": path,
        "name": name,
        "description": description,
        "type": memory_type(fields),
        "bytes": os.path.getsize(path),
        "_text": f"{name or ''} {description or ''} {body}",
    }


def local_link(link):
    """Return the file part of a Markdown link target, or None for an external link or a bare
    anchor. Anchors are dropped so file.md#why still names file.md."""
    if "://" in link or link.startswith(("#", "mailto:")):
        return None
    return link.split("#", 1)[0] or None


def index_health(memory_dir, files):
    index_path = os.path.join(memory_dir, "MEMORY.md")
    if not os.path.isfile(index_path):
        return {"exists": False, "missing_from_index": sorted(files), "dangling_links": []}
    text = read_text(index_path)
    linked = set()
    for link in INDEX_LINK_RE.findall(text):
        target = local_link(link)
        if target and os.path.dirname(os.path.normpath(target)) in ("", "."):
            linked.add(os.path.basename(target))
    return {
        "exists": True,
        "lines": len(text.splitlines()),
        "bytes": len(text.encode("utf-8")),
        "truncated_on_load": len(text.splitlines()) > INDEX_LINE_LIMIT or len(text.encode("utf-8")) > INDEX_BYTE_LIMIT,
        "missing_from_index": sorted(set(files) - linked),
        "dangling_links": sorted(link for link in linked if link not in files),
    }


# ---------- project paths ----------


def path_state(path):
    """Return "exists", "missing" (provably absent), "unmounted", or "unknown". A relative path
    would be checked against the current directory, which proves nothing, so it is unknown."""
    if not os.path.isabs(path):
        return "unknown"
    try:
        os.stat(path)
        return "exists"
    except FileNotFoundError:
        pass
    except OSError:
        return "unknown"
    normal = os.path.normpath(path)
    parents = [parent for parent in VOLUME_PARENTS if normal.startswith(parent + os.sep)]
    if not parents:
        return "missing"
    # On a removable-volume path, the path is gone only if the volume holding it is mounted: some
    # folder between the volume parent and the deepest existing ancestor is then a mount point.
    # Otherwise the drive is unplugged (macOS /Volumes/<label>, Linux /media/<user>/<label>) and
    # the path is kept. If even the volume parent is missing, nothing is mounted there either.
    parent = max(parents, key=len)
    ancestor = os.path.dirname(normal)
    while not os.path.isdir(ancestor):
        ancestor = os.path.dirname(ancestor)
    if ancestor != parent and not ancestor.startswith(parent + os.sep):
        return "unmounted"
    real = os.path.realpath(ancestor)
    if not any(real == p or real.startswith(p + os.sep) for p in VOLUME_PARENTS):
        return "missing"  # resolved off the volume tree, as /Volumes/<system disk> links to /
    probe = real
    while probe not in VOLUME_PARENTS and probe != os.sep:
        if os.path.ismount(probe):
            return "missing"
        probe = os.path.dirname(probe)
    return "unmounted"


def transcript_cwd(path):
    """Return the first cwd recorded in a transcript's first lines, None when there is none, or
    EMPTY when the transcript holds no user or assistant message at all (an empty file, or only
    bookkeeping records), which says nothing about where the project lived."""
    conversation = False
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for _, line in zip(range(TRANSCRIPT_HEAD_LINES), handle):
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(record, dict):
                    continue
                if isinstance(record.get("cwd"), str) and record["cwd"]:
                    return record["cwd"]
                conversation = conversation or record.get("type") in ("user", "assistant")
    except OSError:
        return None
    return None if conversation else EMPTY


def scan_project(project_dir):
    entries = sorted(os.listdir(project_dir))
    transcripts = [e for e in entries if e.endswith(".jsonl") and os.path.isfile(os.path.join(project_dir, e))]
    artifact_dirs = [e for e in entries if session_artifact(project_dir, e) and not e.endswith(".jsonl")]
    recorded = collections.Counter(transcript_cwd(os.path.join(project_dir, t)) for t in transcripts)
    if EMPTY in recorded and len(recorded) > 1:
        del recorded[EMPTY]
    if EMPTY in recorded:
        recorded = collections.Counter({None: recorded[EMPTY]})
    if not transcripts:
        remembered = cleaned_project_path(project_dir)
        if remembered:
            recorded = collections.Counter([remembered])
            transcripts = []
    known = [cwd for cwd, _ in recorded.most_common() if cwd]
    states = {cwd: path_state(cwd) for cwd in known}
    cwd, reason = (known[0] if known else None), None
    # A session that moves into a worktree records the worktree path, so one directory can hold
    # several paths. Any path that still exists keeps the directory live; it is dead only when
    # every transcript names a path and every one of those paths is provably gone.
    if not transcripts and not recorded:
        state, reason = "unknown", "no transcripts"
    elif any(s == "exists" for s in states.values()):
        state = "live"
    elif None in recorded:
        state, reason = "unknown", "a transcript has no cwd"
    elif all(s == "missing" for s in states.values()):
        state = "dead"
    elif any(s == "unmounted" for s in states.values()):
        state = "unmounted"
    else:
        state, reason = "unknown", "a path could not be checked"
    memory_dir = os.path.join(project_dir, "memory")
    memories, index = [], None
    if os.path.isdir(memory_dir):
        names = sorted(f for f in os.listdir(memory_dir) if f.endswith(".md") and f != "MEMORY.md")
        memories = [describe_memory(os.path.join(memory_dir, n)) for n in names]
        index = index_health(memory_dir, names)
    return {
        "dir": os.path.basename(project_dir),
        "cwd": cwd,
        "state": state,
        "reason": reason,
        "transcripts": len(transcripts),
        "artifact_dirs": len(artifact_dirs),
        "memories": memories,
        "index": index,
    }


def cleaned_project_path(project_dir):
    """Return the path cleanup recorded for a project whose transcripts it removed, or None."""
    try:
        with open(os.path.join(project_dir, CLEANED_MARKER), encoding="utf-8") as handle:
            value = json.load(handle).get("cwd")
    except (OSError, ValueError, AttributeError):
        return None
    return value if isinstance(value, str) and value else None


def load_claude_json(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except ValueError as error:
        sys.exit(f"{path} is not valid JSON ({error}); nothing was changed")
    if not isinstance(data, dict):
        sys.exit(f"{path} does not hold a JSON object; nothing was changed")
    return data


def claude_json_report(path):
    data = load_claude_json(path)
    if data is None:
        return {"path": path, "exists": False}
    report = {"path": path, "exists": True, "entries": 0, "dead": [], "unmounted": [], "unknown": []}
    projects = data.get("projects") if isinstance(data.get("projects"), dict) else {}
    for project_path in projects:
        report["entries"] += 1
        state = path_state(project_path)
        key = {"missing": "dead", "unmounted": "unmounted", "unknown": "unknown"}.get(state)
        if key:
            report[key].append(project_path)
    return report


# ---------- shared tree ----------


def tree_files(tree):
    """Return tree-relative paths of every Markdown file in the tree, skipping dot entries."""
    found = []
    if not os.path.isdir(tree):
        return found
    for current, dirs, files in os.walk(tree):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(files):
            if name.endswith(".md") and not name.startswith("."):
                found.append(os.path.relpath(os.path.join(current, name), tree))
    return found


def tree_location_ok(relative):
    parts = relative.split(os.sep)
    if len(parts) == 1:
        return parts[0] in TREE_ROOT_FILES
    return len(parts) == 2 and parts[0] in TREE_DIRS and parts[1].endswith(".md")


def check_tree_file(tree, relative):
    path = os.path.join(tree, relative)
    text = read_text(path)
    fields, _ = parse_frontmatter(text)
    size = os.path.getsize(path)
    stem = os.path.splitext(os.path.basename(relative))[0]
    if not tree_location_ok(relative):
        return {"path": relative, "bytes": size, "problems": [], "ignored": True}
    problems = []
    if not fields:
        problems.append("no frontmatter")
    else:
        if fields.get("name") != stem:
            problems.append(f"frontmatter name is not the file stem '{stem}'")
        if not isinstance(fields.get("description"), str) or not fields.get("description"):
            problems.append("no description")
    if size > WEB_FILE_BYTE_CAP:
        problems.append(f"{size} bytes, over the {WEB_FILE_BYTE_CAP}-byte cap")
    return {"path": relative, "bytes": size, "problems": problems, "ignored": False}


# ---------- near-duplicates ----------


def words(text):
    """Content words of a memory: lowercase, stopwords and short words dropped, trailing s
    stripped so plurals match."""
    return [w.rstrip("s") for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in STOPWORDS]


def near_duplicates(items):
    """items: list of (location, path, text). Score every cross-location pair by cosine
    similarity of word counts weighted by smoothed IDF, so words common to many memories count
    for less while identical memories still score 1.0 in a small collection.
    Return pairs at or over the threshold, highest first."""
    counts = [collections.Counter(words(text)) for _, _, text in items]
    document_frequency = collections.Counter(word for count in counts for word in count)
    total = len(items)
    vectors = []
    for count in counts:
        vector = {w: n * (math.log((1 + total) / (1 + document_frequency[w])) + 1) for w, n in count.items()}
        vectors.append((vector, math.sqrt(sum(v * v for v in vector.values()))))
    pairs = []
    for i, (loc_a, path_a, _) in enumerate(items):
        vec_a, norm_a = vectors[i]
        for j in range(i + 1, total):
            loc_b, path_b, _ = items[j]
            vec_b, norm_b = vectors[j]
            if loc_a == loc_b or not norm_a or not norm_b:
                continue
            score = sum(v * vec_b.get(w, 0.0) for w, v in vec_a.items()) / (norm_a * norm_b)
            if score >= DUPLICATE_THRESHOLD:
                pairs.append({"a": path_a, "b": path_b, "score": round(score, 2)})
    return sorted(pairs, key=lambda pair: -pair["score"])


# ---------- commands ----------


def projects_root(args):
    return os.path.join(args.claude_dir, "projects")


def scan_all_projects(args):
    root = projects_root(args)
    if not os.path.isdir(root):
        return []
    return [scan_project(os.path.join(root, d)) for d in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, d))]


def command_inventory(args):
    projects = scan_all_projects(args)
    items = []
    for project in projects:
        for memory in project["memories"]:
            items.append((project["dir"], memory["path"], memory.pop("_text")))
    tree_report = []
    for relative in tree_files(args.tree):
        info = describe_memory(os.path.join(args.tree, relative))
        items.append(("tree", info["path"], info.pop("_text")))
        tree_report.append({"path": relative, "name": info["name"], "description": info["description"], "bytes": info["bytes"]})
    report = {
        "projects": projects,
        "tree": {"path": args.tree, "exists": os.path.isdir(args.tree), "files": tree_report},
        "duplicates": near_duplicates(items),
        "claude_json": claude_json_report(args.claude_json),
    }
    if args.json:
        print(json.dumps(report, indent=2))
        return
    with_memory = [p for p in projects if p["memories"]]
    print(f"{len(projects)} project directories; {len(with_memory)} with memory "
          f"({sum(len(p['memories']) for p in projects)} files)")
    for state in ("live", "dead", "unmounted", "unknown"):
        group = [p for p in projects if p["state"] == state]
        if group:
            print(f"  {state}: {len(group)}")
    print("\nMemory by project:")
    for project in with_memory:
        print(f"  {project['cwd'] or project['dir']} [{project['state']}]: {len(project['memories'])} files")
        index = project["index"]
        for file in index["missing_from_index"]:
            print(f"    not in MEMORY.md: {file}")
        for link in index["dangling_links"]:
            print(f"    MEMORY.md links to missing file: {link}")
        if index.get("truncated_on_load"):
            print(f"    MEMORY.md is over {INDEX_LINE_LIMIT} lines or {INDEX_BYTE_LIMIT} bytes and loads truncated")
    print(f"\nShared tree {args.tree}: " + (f"{len(tree_report)} files" if report["tree"]["exists"] else "does not exist"))
    print(f"\nNear-duplicates (score >= {DUPLICATE_THRESHOLD}): {len(report['duplicates'])}")
    for pair in report["duplicates"]:
        print(f"  {pair['score']}  {pair['a']}\n        {pair['b']}")
    claude_json = report["claude_json"]
    if claude_json["exists"]:
        print(f"\n{claude_json['path']}: {claude_json['entries']} project entries, {len(claude_json['dead'])} dead, "
              f"{len(claude_json['unmounted'])} on unmounted volumes, {len(claude_json['unknown'])} unknown")


def removable_source(args, source):
    """Exit unless source is a memory file inside a project memory directory (not MEMORY.md)."""
    source = checked_arg_path(source, "plan source")
    memory_dir = os.path.dirname(source)
    project_dir = os.path.dirname(memory_dir)
    if (os.path.basename(memory_dir) != "memory" or os.path.dirname(project_dir) != projects_root(args)
            or not source.endswith(".md") or os.path.basename(source) == "MEMORY.md"):
        sys.exit(f"plan source is not a project memory file: {source}")
    if not os.path.isfile(source):
        sys.exit(f"plan source does not exist: {source}")
    return source


def rename_frontmatter(text, name):
    """Set the top-level frontmatter name to the given file stem, adding frontmatter if there is
    none, since Claude app memory resolves links by a file's name and expects it to be its stem."""
    header, rest = split_frontmatter(text)
    if header is None:
        return f"---\nname: {name}\n---\n\n{rest}"
    if re.search(r"^name:.*$", header, flags=re.MULTILINE):
        header = re.sub(r"^name:.*$", f"name: {name}", header, count=1, flags=re.MULTILINE)
    else:
        header = f"name: {name}\n{header}"
    return f"---\n{header}{rest}"


def existing_ancestor(path):
    while not os.path.isdir(path):
        path = os.path.dirname(path)
    return path


def require_writable(directories):
    """Exit before changing anything unless a file can be created in every directory. A sandboxed
    session can forbid writes under ~/.claude, and finding that out partway through a run would
    leave a memory copied into the tree with its project copy still in place."""
    blocked = []
    for directory in sorted(directories):
        try:
            descriptor, probe = tempfile.mkstemp(prefix=".consolidate-check-", dir=directory)
            os.close(descriptor)
            os.unlink(probe)
        except OSError as error:
            blocked.append(f"{directory} ({error.strerror})")
    if blocked:
        sys.exit("cannot write to " + "; ".join(blocked) + ". nothing was changed. If a sandbox blocks "
                 "these writes, run the same command from a terminal outside the sandbox.")


def remove_index_link(index_path, filename):
    """Remove MEMORY.md lines that link to filename in the same directory and to nothing else.
    Returns (lines removed, lines left because they also link other files)."""
    if not os.path.isfile(index_path):
        return 0, 0
    lines = read_text(index_path).splitlines(keepends=True)
    kept, removed, shared = [], 0, 0
    for line in lines:
        targets = [local_link(link) for link in INDEX_LINK_RE.findall(line)]
        files = {os.path.normpath(t) for t in targets if t}
        if filename in files and files == {filename}:
            removed += 1
            continue
        if filename in files:
            shared += 1
        kept.append(line)
    if removed:
        write_atomic(index_path, "".join(kept), os.stat(index_path).st_mode & 0o777)
    return removed, shared


def write_atomic(path, text, mode=None):
    descriptor, temporary = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise


def command_promote(args):
    try:
        with open(input_path(args.plan, "--plan"), encoding="utf-8") as handle:
            plan = json.load(handle)
    except OSError as error:
        sys.exit(f"cannot read --plan: {error}")
    except ValueError as error:
        sys.exit(f"--plan is not valid JSON: {error}")
    if not isinstance(plan, list) or not plan:
        sys.exit("--plan must be a non-empty JSON list")
    steps, targets, sources = [], set(), set()
    for row in plan:
        if not isinstance(row, dict):
            sys.exit(f"each plan row must be an object with action, source, and target: {row!r}")
        action, target = row.get("action"), row.get("target", "")
        source = removable_source(args, row.get("source", ""))
        if source in sources:
            sys.exit(f"plan lists the same source twice: {source}")
        sources.add(source)
        target_rel = os.path.normpath(target) if isinstance(target, str) and target else ""
        if action not in ("move", "remove"):
            sys.exit(f"unknown action {action!r} for {source}")
        if target_rel.startswith("..") or os.path.isabs(target_rel) or not tree_location_ok(target_rel):
            sys.exit(f"target is not a tree location (profile.md, preferences.md, topics/, areas/, people/): {target}")
        target_path = os.path.join(args.tree, target_rel)
        if action == "move":
            if os.path.lexists(target_path) or target_rel in targets:
                sys.exit(f"target already exists, so it would be overwritten: {target_rel}")
            targets.add(target_rel)
        elif not os.path.isfile(target_path) and target_rel not in targets:
            sys.exit(f"remove needs its merged target to exist already or to be created by an "
                     f"earlier move in this plan: {target_rel}")
        steps.append((action, source, target_rel, target_path))
    if args.apply:
        directories = {os.path.dirname(source) for _, source, _, _ in steps} | {args.claude_dir}
        directories.add(existing_ancestor(args.tree))
        require_writable(directories)
    backup_root = unique_directory(os.path.join(args.claude_dir, "memory-backups", timestamp())) if args.apply else None
    for number, (action, source, target_rel, target_path) in enumerate(steps, 1):
        verb = "copy to tree and remove" if action == "move" else "remove (merged into tree)"
        print(f"{'' if args.apply else 'would '}{verb}: {source} -> {target_rel}")
        if not args.apply:
            continue
        try:
            promote_step(action, source, target_rel, target_path, backup_root)
        except OSError as error:
            sys.exit(f"step {number} of {len(steps)} failed ({error}); steps before it were applied, and "
                     f"backups are in {backup_root}. Fix the cause, remove the finished rows from the plan "
                     f"(and if {target_rel} was already written, change this row's action to remove), "
                     "then run it again.")
    if not args.apply:
        print("dry run. re-run with --apply to make these changes.")


def promote_step(action, source, target_rel, target_path, backup_root):
    if action == "move":
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "x", encoding="utf-8") as out:
            out.write(rename_frontmatter(read_text(source), os.path.splitext(os.path.basename(target_rel))[0]))
    project = os.path.basename(os.path.dirname(os.path.dirname(source)))
    backup_dir = os.path.join(backup_root, project)
    os.makedirs(backup_dir, exist_ok=True)
    index_path = os.path.join(os.path.dirname(source), "MEMORY.md")
    if os.path.isfile(index_path) and not os.path.exists(os.path.join(backup_dir, "MEMORY.md")):
        shutil.copy2(index_path, os.path.join(backup_dir, "MEMORY.md"))
    shutil.move(source, os.path.join(backup_dir, os.path.basename(source)))
    removed, left = remove_index_link(index_path, os.path.basename(source))
    note = f"; {left} MEMORY.md line(s) also link other files, so edit them by hand" if left else ""
    print(f"  backed up to {backup_dir}; removed {removed} MEMORY.md line(s){note}")


def unique_directory(path):
    """Create and return path, or path-2, path-3, ... if it exists, so two runs in the same second
    never share a backup directory."""
    candidate, number = path, 1
    while True:
        try:
            os.makedirs(candidate)
            return candidate
        except FileExistsError:
            number += 1
            candidate = f"{path}-{number}"


def own_ancestor_pids():
    pids, pid = set(), os.getpid()
    while pid > 1 and pid not in pids:
        pids.add(pid)
        try:
            output = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)], capture_output=True, text=True, check=True).stdout
            pid = int(output.strip())
        except (OSError, subprocess.CalledProcessError, ValueError):
            break
    return pids


def other_claude_sessions():
    """Return PIDs of Claude Code processes that are not this script's own ancestors, or None
    when processes can't be listed (a sandbox can forbid running ps)."""
    try:
        output = subprocess.run(["ps", "-axo", "pid=,comm="], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    ancestors = own_ancestor_pids()
    found = []
    for line in output.splitlines():
        pid_text, _, command = line.strip().partition(" ")
        pid = int(pid_text)
        name = os.path.basename(command.strip())
        if pid in ancestors or name not in CLAUDE_NAMES + SCRIPT_HOSTS:
            continue
        if name in SCRIPT_HOSTS and not runs_claude_script(pid):
            continue
        found.append(pid)
    return found


def runs_claude_script(pid):
    """True when a node or bun process runs a script named claude, as an npm install does."""
    try:
        arguments = subprocess.run(["ps", "-o", "args=", "-p", str(pid)], capture_output=True, text=True,
                                   check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return False
    return len(arguments) > 1 and os.path.basename(arguments[1]) in CLAUDE_NAMES


def session_artifact(project_dir, name):
    """True for a transcript (*.jsonl) or anything named after a session id: a session directory,
    or a side file such as <session-id>.desktop-released.json."""
    if name.endswith(".jsonl") and os.path.isfile(os.path.join(project_dir, name)):
        return True
    return bool(UUID_RE.match(name.split(".", 1)[0]))


def remove_artifacts(project_dir):
    """Quarantine then delete a dead project's transcripts and session artifacts. Returns
    (removed count, whether the project directory remains and with what)."""
    entries = os.listdir(project_dir)
    artifacts = [e for e in entries if session_artifact(project_dir, e)]
    quarantine = tempfile.mkdtemp(prefix=".consolidate-delete-", dir=project_dir)
    for name in artifacts:
        os.rename(os.path.join(project_dir, name), os.path.join(quarantine, name))
    shutil.rmtree(quarantine)
    remaining = [e for e in os.listdir(project_dir) if e != CLEANED_MARKER]
    if not remaining:
        if os.path.exists(os.path.join(project_dir, CLEANED_MARKER)):
            os.unlink(os.path.join(project_dir, CLEANED_MARKER))
        os.rmdir(project_dir)
    return len(artifacts), remaining


def command_cleanup(args):
    projects = scan_all_projects(args)
    all_dead = [p for p in projects if p["state"] == "dead"]
    claude_json = claude_json_report(args.claude_json)
    dead_entries = claude_json.get("dead", [])
    # A dead project cleaned earlier keeps only memory/ and has nothing left to remove, so it is
    # left out of both the work and the mass-deletion share below.
    dead_dirs = [p for p in all_dead if p["transcripts"] or p["artifact_dirs"]]
    cleaned = {p["dir"] for p in all_dead if p not in dead_dirs}
    resolvable = [p for p in projects if p["state"] in ("live", "dead", "unmounted") and p["dir"] not in cleaned]
    for project in dead_dirs:
        memory_dir = os.path.join(projects_root(args), project["dir"], "memory")
        keep = " (memory/ kept)" if os.path.isdir(memory_dir) else ""
        print(f"{'' if args.apply else 'would '}remove {project['transcripts']} transcripts and "
              f"{project['artifact_dirs']} session dirs: {project['dir']} (was {project['cwd']}){keep}")
    for entry in dead_entries:
        print(f"{'' if args.apply else 'would '}remove {args.claude_json} entry: {entry}")
    for project in projects:
        if project["state"] == "unmounted":
            print(f"keep {project['dir']}: {project['cwd']} is on a volume that is not mounted")
        elif project["state"] == "unknown":
            print(f"keep {project['dir']}: its path is unknown ({project['reason']})")
    if not dead_dirs and not dead_entries:
        print("nothing to remove.")
        return
    if not args.apply:
        print("dry run. re-run with --apply to make these changes.")
        return
    if dead_entries and args.claude_json_is_link:
        sys.exit(f"refusing to apply: {args.claude_json} is reached through a symlink, so nothing was "
                 "removed (transcripts included); pass --claude-json with the resolved path to change it")
    directories = {os.path.join(projects_root(args), p["dir"]) for p in dead_dirs}
    if dead_entries:
        directories.add(os.path.dirname(args.claude_json))
    require_writable(directories)
    refusals = []
    if not args.ignore_sessions:
        sessions = other_claude_sessions()
        if sessions is None:
            refusals.append("could not list running processes to check for other Claude sessions, which "
                            "can write their old copy of ~/.claude.json back (--ignore-sessions overrides)")
        elif sessions:
            refusals.append(f"other Claude sessions are running (pids {', '.join(map(str, sessions))}), and "
                            "a running session can write its old copy of ~/.claude.json back "
                            "(--ignore-sessions overrides)")
    if not args.force:
        for label, dead, total in (("project directories", len(dead_dirs), len(resolvable)),
                                   (f"{args.claude_json} entries", len(dead_entries), claude_json.get("entries", 0))):
            if dead >= MASS_DELETION_MINIMUM and total and dead / total >= MASS_DELETION_SHARE:
                refusals.append(f"{dead} of {total} {label} look dead, which usually means the wrong machine "
                                "or an unmounted volume (--force overrides)")
    if refusals:
        sys.exit("refusing to apply: " + "; ".join(refusals) + ".")
    for project in dead_dirs:
        project_dir = os.path.join(projects_root(args), project["dir"])
        removed, remaining = remove_artifacts(project_dir)
        if remaining:
            # The folder stays (memory/, or a file this script doesn't know), so record where the
            # project lived; without a transcript, later runs could no longer tell.
            write_atomic(os.path.join(project_dir, CLEANED_MARKER),
                         json.dumps({"cwd": project["cwd"], "cleaned": timestamp()}) + "\n")
        kept = "; memory/ kept" if "memory" in remaining else ""
        others = [e for e in remaining if e != "memory"]
        note = f"; left {', '.join(others)}" if others else ""
        print(f"removed {removed} items from {project['dir']}{kept}{note}")
    if dead_entries:
        prune_claude_json(args, set(dead_entries))


def prune_claude_json(args, dead):
    path = args.claude_json
    if args.claude_json_is_link:
        sys.exit(f"{path} is the target of a symlinked config; pass --claude-json with that path to change it")
    data = load_claude_json(path)
    projects = data.get("projects") or {}
    removable = [p for p in projects if p in dead and path_state(p) == "missing"]
    if not removable:
        return
    mode = os.stat(path).st_mode & 0o777
    backup, number = f"{path}.backup-{timestamp()}", 1
    while True:
        try:
            descriptor = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            break
        except FileExistsError:
            number += 1
            backup = f"{path}.backup-{timestamp()}-{number}"
    with os.fdopen(descriptor, "wb") as out, open(path, "rb") as source:
        shutil.copyfileobj(source, out)
    for project_path in removable:
        del projects[project_path]
    write_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", mode)
    print(f"removed {len(removable)} entries from {path}; backup at {backup}")


def command_seed(args):
    export = input_path(args.source, "--from")
    if not os.path.isdir(export):
        sys.exit(f"--from is not a directory: {export}")
    copies, skipped = [], []
    for relative in tree_files(export):
        if not tree_location_ok(relative):
            skipped.append((relative, "not a Claude app memory location"))
        elif os.path.lexists(os.path.join(args.tree, relative)):
            skipped.append((relative, "already in the tree"))
        else:
            copies.append(relative)
    for relative in copies:
        print(f"{'' if args.apply else 'would '}copy {relative}")
        if args.apply:
            target = os.path.join(args.tree, relative)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "x", encoding="utf-8") as out:
                out.write(read_text(os.path.join(export, relative)))
    for relative, reason in skipped:
        print(f"skip {relative}: {reason}")
    if not args.apply:
        print("dry run. re-run with --apply to make these changes.")


def command_check_tree(args):
    if not os.path.isdir(args.tree):
        sys.exit(f"tree does not exist: {args.tree}")
    results = [check_tree_file(args.tree, relative) for relative in tree_files(args.tree)]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            status = "not a Claude app memory location, so not synced" if result["ignored"] else (
                "; ".join(result["problems"]) or "ok")
            print(f"{result['path']} ({result['bytes']} bytes): {status}")
    if any(result["problems"] for result in results):
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--claude-dir", default="~/.claude")
    parser.add_argument("--claude-json", default="~/.claude.json")
    parser.add_argument("--tree", default=None,
                        help="the shared tree (default: memories in iCloud Drive, else ~/Documents, else ~)")
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory")
    inventory.add_argument("--json", action="store_true")
    promote = commands.add_parser("promote")
    promote.add_argument("--plan", required=True)
    promote.add_argument("--apply", action="store_true")
    cleanup = commands.add_parser("cleanup")
    cleanup.add_argument("--apply", action="store_true")
    cleanup.add_argument("--ignore-sessions", action="store_true")
    cleanup.add_argument("--force", action="store_true")
    seed = commands.add_parser("seed")
    seed.add_argument("--from", dest="source", required=True)
    seed.add_argument("--apply", action="store_true")
    check = commands.add_parser("check-tree")
    check.add_argument("--json", action="store_true")
    args = parser.parse_args()
    args.claude_json_is_link = os.path.islink(os.path.expanduser(args.claude_json))
    args.claude_dir = checked_arg_path(args.claude_dir, "--claude-dir")
    args.claude_json = checked_arg_path(args.claude_json, "--claude-json")
    args.tree = checked_arg_path(args.tree or default_tree(), "--tree")
    if args.tree == os.path.realpath(os.path.expanduser("~")):
        sys.exit("--tree must be a folder inside your home directory, not the home directory itself")
    {"inventory": command_inventory, "promote": command_promote, "cleanup": command_cleanup,
     "seed": command_seed, "check-tree": command_check_tree}[args.command](args)


if __name__ == "__main__":
    main()
