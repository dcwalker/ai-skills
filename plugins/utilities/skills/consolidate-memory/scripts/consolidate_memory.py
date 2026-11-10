#!/usr/bin/env python3
"""Inventory, promote, and clean up Claude Code memory across projects, and check the shared tree.

Claude Code keeps one directory per project under <claude-dir>/projects/, named with a lossy
slug of the project path. Each holds session transcripts (*.jsonl, plus UUID-named artifact
directories) and, for some projects, auto memory in memory/ with a MEMORY.md index. The shared
tree (--tree, default ~/memories) uses the same layout as Claude app memory: profile.md,
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
for another reason, or sits on a volume that is not mounted, is kept. Cleanup never deletes a
memory/ directory, backs up ~/.claude.json before rewriting it, and refuses while another Claude
session is running or when nearly everything looks dead, unless passed --force.

Usage:
  consolidate_memory.py inventory [--json]
  consolidate_memory.py promote --plan plan.json [--apply]
  consolidate_memory.py cleanup [--apply] [--force]
  consolidate_memory.py seed --from EXPORT_DIR [--apply]
  consolidate_memory.py check-tree [--json]

Common options: --claude-dir (default ~/.claude), --claude-json (default ~/.claude.json),
--tree (default ~/memories). Every path option must be inside the home or temp directory.

A promotion plan is a JSON list of objects:
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
VOLUME_PARENTS = ("/Volumes", "/Network", "/mnt", "/media", "/run/media")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
INDEX_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def checked_arg_path(path, option):
    """Resolve a command-line path, exiting unless it is under the home or temp directory."""
    resolved = os.path.realpath(os.path.expanduser(path))
    for base in (os.path.expanduser("~"), tempfile.gettempdir(), "/tmp", "/private/tmp"):
        base = os.path.realpath(base)
        if resolved == base or resolved.startswith(base + os.sep):
            return resolved
    sys.exit(f"{option} must be inside your home directory or the temp directory: {path}")


def timestamp():
    return datetime.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")


# ---------- frontmatter and memory files ----------


def parse_frontmatter(text):
    """Parse the YAML-subset frontmatter Claude memory files use: top-level keys and one level
    of nested keys (such as metadata.type). Returns (fields, body)."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    fields, parent = {}, None
    for line in text[4:end].splitlines():
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
        elif value:
            fields[key], parent = value, None
        else:
            fields[key], parent = {}, key
    body = text[end + 4 :].lstrip("\n")
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
        "bytes": len(text.encode("utf-8")),
        "_text": f"{name or ''} {description or ''} {body}",
    }


def index_health(memory_dir, files):
    index_path = os.path.join(memory_dir, "MEMORY.md")
    if not os.path.isfile(index_path):
        return {"exists": False, "missing_from_index": sorted(files), "dangling_links": []}
    text = read_text(index_path)
    linked = {os.path.basename(link) for link in INDEX_LINK_RE.findall(text)}
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
    """Return "exists", "missing" (provably absent), "unmounted", or "unknown"."""
    try:
        os.stat(path)
        return "exists"
    except FileNotFoundError:
        pass
    except OSError:
        return "unknown"
    parts = os.path.normpath(path).split(os.sep)
    for parent in VOLUME_PARENTS:
        depth = len(parent.split(os.sep))
        if (os.sep.join(parts[:depth]) == parent and len(parts) > depth
                and not os.path.isdir(os.sep.join(parts[: depth + 1]))):
            return "unmounted"
    return "missing"


def transcript_cwd(path):
    """Return the first cwd recorded in a transcript's first lines, or None."""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for _, line in zip(range(TRANSCRIPT_HEAD_LINES), handle):
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if isinstance(record, dict) and isinstance(record.get("cwd"), str) and record["cwd"]:
                    return record["cwd"]
    except OSError:
        return None
    return None


def scan_project(project_dir):
    entries = sorted(os.listdir(project_dir))
    transcripts = [e for e in entries if e.endswith(".jsonl") and os.path.isfile(os.path.join(project_dir, e))]
    artifact_dirs = [e for e in entries if UUID_RE.match(e) and os.path.isdir(os.path.join(project_dir, e))]
    recorded = collections.Counter(transcript_cwd(os.path.join(project_dir, t)) for t in transcripts)
    known = [cwd for cwd, _ in recorded.most_common() if cwd]
    states = {cwd: path_state(cwd) for cwd in known}
    cwd, reason = (known[0] if known else None), None
    # A session that moves into a worktree records the worktree path, so one directory can hold
    # several paths. Any path that still exists keeps the directory live; it is dead only when
    # every transcript names a path and every one of those paths is provably gone.
    if not transcripts:
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


def load_claude_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def claude_json_report(path):
    data = load_claude_json(path)
    if data is None:
        return {"path": path, "exists": False}
    report = {"path": path, "exists": True, "entries": 0, "dead": [], "unmounted": [], "unknown": []}
    for project_path in (data.get("projects") or {}):
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
    size = len(text.encode("utf-8"))
    stem = os.path.splitext(os.path.basename(relative))[0]
    problems = []
    if not tree_location_ok(relative):
        problems.append("not in a location Claude app memory uses")
    if not fields:
        problems.append("no frontmatter")
    else:
        if fields.get("name") != stem:
            problems.append(f"frontmatter name is not the file stem '{stem}'")
        if not isinstance(fields.get("description"), str) or not fields.get("description"):
            problems.append("no description")
    if size > WEB_FILE_BYTE_CAP:
        problems.append(f"{size} bytes, over the {WEB_FILE_BYTE_CAP}-byte cap")
    return {"path": relative, "bytes": size, "problems": problems}


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


def remove_index_lines(index_path, filename):
    if not os.path.isfile(index_path):
        return 0
    lines = read_text(index_path).splitlines(keepends=True)
    kept = [line for line in lines if filename not in {os.path.basename(link) for link in INDEX_LINK_RE.findall(line)}]
    if len(kept) != len(lines):
        write_atomic(index_path, "".join(kept))
    return len(lines) - len(kept)


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
    with open(checked_arg_path(args.plan, "--plan"), encoding="utf-8") as handle:
        plan = json.load(handle)
    if not isinstance(plan, list) or not plan:
        sys.exit("--plan must be a non-empty JSON list")
    steps, targets = [], set()
    for row in plan:
        action, target = row.get("action"), row.get("target", "")
        source = removable_source(args, row.get("source", ""))
        target_rel = os.path.normpath(target)
        if action not in ("move", "remove"):
            sys.exit(f"unknown action {action!r} for {source}")
        if target_rel.startswith("..") or os.path.isabs(target_rel) or not tree_location_ok(target_rel):
            sys.exit(f"target is not a tree location (profile.md, preferences.md, topics/, areas/, people/): {target}")
        target_path = os.path.join(args.tree, target_rel)
        if action == "move":
            if os.path.lexists(target_path) or target_rel in targets:
                sys.exit(f"target already exists, so it would be overwritten: {target_rel}")
            targets.add(target_rel)
        elif not os.path.isfile(target_path):
            sys.exit(f"remove needs the merged target to exist first: {target_rel}")
        steps.append((action, source, target_rel, target_path))
    backup_root = os.path.join(args.claude_dir, "memory-backups", timestamp())
    for action, source, target_rel, target_path in steps:
        verb = "copy to tree and remove" if action == "move" else "remove (merged into tree)"
        print(f"{'' if args.apply else 'would '}{verb}: {source} -> {target_rel}")
        if not args.apply:
            continue
        if action == "move":
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "x", encoding="utf-8") as out:
                out.write(read_text(source))
        project = os.path.basename(os.path.dirname(os.path.dirname(source)))
        backup_dir = os.path.join(backup_root, project)
        os.makedirs(backup_dir, exist_ok=True)
        index_path = os.path.join(os.path.dirname(source), "MEMORY.md")
        if os.path.isfile(index_path) and not os.path.exists(os.path.join(backup_dir, "MEMORY.md")):
            shutil.copy2(index_path, os.path.join(backup_dir, "MEMORY.md"))
        shutil.move(source, os.path.join(backup_dir, os.path.basename(source)))
        removed = remove_index_lines(index_path, os.path.basename(source))
        print(f"  backed up to {backup_dir}; removed {removed} MEMORY.md line(s)")
    if not args.apply:
        print("dry run. re-run with --apply to make these changes.")


def own_ancestor_pids():
    pids, pid = set(), os.getpid()
    while pid > 1 and pid not in pids:
        pids.add(pid)
        try:
            output = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)], capture_output=True, text=True, check=True).stdout
            pid = int(output.strip())
        except (subprocess.CalledProcessError, ValueError):
            break
    return pids


def other_claude_sessions():
    """Return PIDs of Claude Code processes that are not this script's own ancestors."""
    output = subprocess.run(["ps", "-axo", "pid=,comm="], capture_output=True, text=True, check=True).stdout
    ancestors = own_ancestor_pids()
    found = []
    for line in output.splitlines():
        pid_text, _, command = line.strip().partition(" ")
        if os.path.basename(command.strip()) in ("claude", "claude-code") and int(pid_text) not in ancestors:
            found.append(int(pid_text))
    return found


def remove_artifacts(project_dir):
    """Quarantine then delete a dead project's transcripts and session directories. Returns
    (removed count, whether memory/ remains)."""
    entries = os.listdir(project_dir)
    artifacts = [e for e in entries if (e.endswith(".jsonl") and os.path.isfile(os.path.join(project_dir, e)))
                 or (UUID_RE.match(e) and os.path.isdir(os.path.join(project_dir, e)))]
    quarantine = tempfile.mkdtemp(prefix=".consolidate-delete-", dir=project_dir)
    for name in artifacts:
        os.rename(os.path.join(project_dir, name), os.path.join(quarantine, name))
    shutil.rmtree(quarantine)
    remaining = os.listdir(project_dir)
    if not remaining:
        os.rmdir(project_dir)
    return len(artifacts), "memory" in remaining


def command_cleanup(args):
    projects = scan_all_projects(args)
    dead_dirs = [p for p in projects if p["state"] == "dead"]
    resolvable = [p for p in projects if p["state"] in ("live", "dead", "unmounted")]
    claude_json = claude_json_report(args.claude_json)
    dead_entries = claude_json.get("dead", [])
    for project in dead_dirs:
        keep = " (memory/ kept)" if project["memories"] or project["index"] else ""
        print(f"{'' if args.apply else 'would '}remove {project['transcripts']} transcripts and "
              f"{project['artifact_dirs']} session dirs: {project['dir']} (was {project['cwd']}){keep}")
    for entry in dead_entries:
        print(f"{'' if args.apply else 'would '}remove ~/.claude.json entry: {entry}")
    kept = [p for p in projects if p["state"] in ("unknown", "unmounted")]
    if kept:
        print(f"kept {len(kept)} directories whose path is unknown or on an unmounted volume")
    if not args.apply:
        print("dry run. re-run with --apply to make these changes.")
        return
    refusals = []
    if dead_entries and args.claude_json_is_link:
        sys.exit(f"refusing to apply: {args.claude_json} is reached through a symlink; "
                 "pass --claude-json with the resolved path to change it")
    if not args.force:
        sessions = other_claude_sessions()
        if sessions:
            refusals.append(f"other Claude sessions are running (pids {', '.join(map(str, sessions))}); "
                            "a running session can write its old ~/.claude.json back")
        for label, dead, total in (("project directories", len(dead_dirs), len(resolvable)),
                                   ("~/.claude.json entries", len(dead_entries), claude_json.get("entries", 0))):
            if dead >= MASS_DELETION_MINIMUM and total and dead / total >= MASS_DELETION_SHARE:
                refusals.append(f"{dead} of {total} {label} look dead, which usually means the wrong machine "
                                "or an unmounted volume")
    if refusals:
        sys.exit("refusing to apply: " + "; ".join(refusals) + ". re-run with --force to override.")
    for project in dead_dirs:
        removed, memory_kept = remove_artifacts(os.path.join(projects_root(args), project["dir"]))
        print(f"removed {removed} items from {project['dir']}" + ("; memory/ kept" if memory_kept else ""))
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
    backup = f"{path}.backup-{timestamp()}"
    shutil.copyfile(path, backup)
    os.chmod(backup, 0o600)
    for project_path in removable:
        del projects[project_path]
    write_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", mode)
    print(f"removed {len(removable)} entries from {path}; backup at {backup}")


def command_seed(args):
    export = checked_arg_path(args.source, "--from")
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
            status = "; ".join(result["problems"]) or "ok"
            print(f"{result['path']} ({result['bytes']} bytes): {status}")
    if any(result["problems"] for result in results):
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--claude-dir", default="~/.claude")
    parser.add_argument("--claude-json", default="~/.claude.json")
    parser.add_argument("--tree", default="~/memories")
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory")
    inventory.add_argument("--json", action="store_true")
    promote = commands.add_parser("promote")
    promote.add_argument("--plan", required=True)
    promote.add_argument("--apply", action="store_true")
    cleanup = commands.add_parser("cleanup")
    cleanup.add_argument("--apply", action="store_true")
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
    args.tree = checked_arg_path(args.tree, "--tree")
    {"inventory": command_inventory, "promote": command_promote, "cleanup": command_cleanup,
     "seed": command_seed, "check-tree": command_check_tree}[args.command](args)


if __name__ == "__main__":
    main()
