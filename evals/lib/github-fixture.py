#!/usr/bin/env python3
"""Stand up a fake GitHub for one trial: repos, checkouts, and a gh cassette.

A skill that keeps its data in a GitHub repository (sift-email's rubric and
state files) needs three things from GitHub during a trial: repositories it
can clone, pull, and push; checkouts beside the working directory, the way a
cloud routine clones each attached repository; and `gh` answers about who the
user is, which repositories they own, and where a file's content turns up in
a code search. This script builds all three from one fixture file,
github-fixture.json, so no trial can reach the real GitHub.

Fixture format (dates and {{...}} tokens resolve like any stub state; see
fixture-dates.py, which this script's input has already been through):

{
  "anchor_date": "2026-10-10",
  "login": "pat-example",                 // the authenticated user, or null
                                          // for a gh that is not logged in
  "repos": {
    "pat-example/files": {
      "private": true,
      "checkout": true,                   // cloned beside the workspace, as a
                                          // routine clones an attached repo
      "files": {"sift-email/rubric.md": "...", ...}
    },
    "riley-sample/files": {"private": true, "files": {...}}
  }
}

Each repository becomes a bare git repository at
<run-dir>/github/git/<owner>/<name> (with a <name>.git alias), and a
checkout's origin points there, so its owner and name are the last two parts
of the remote URL, as they are behind a cloud session's git proxy. Clones of
https://github.com/<owner>/<name> resolve to the same place through a
url.insteadOf rule the harness exports.

The cassette answers:
  gh api user                         -> the login
  gh api repos/<owner>/<name>         -> owner, name, visibility, default branch
  gh repo view <owner>/<name>         -> the same, in gh's --json field names
  gh search code ... / gh api search/code?...
      scoped to the login (--owner <login>, user:<login>, owner:<login>)
                                      -> matches in the login's repos only
      unscoped                        -> matches in every repo, other users'
                                         included, so a skill that searches
                                         all of GitHub sees someone else's file
A match is any repository file containing a search term (the quoted phrase,
or the query's words) as plain text.

Usage:
  github-fixture.py setup <github-seed.json> <run-dir> <checkouts-dir>
      Build the repositories and checkouts; write <run-dir>/gh-cassette.json.
  github-fixture.py snapshot <github-seed.json> <run-dir> <out.json>
      Record each repository's commits and files at HEAD after the trial.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

DEFAULT_BRANCH = "main"
GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "GIT_AUTHOR_NAME": "Fixture",
    "GIT_AUTHOR_EMAIL": "fixture@localhost",
    "GIT_COMMITTER_NAME": "Fixture",
    "GIT_COMMITTER_EMAIL": "fixture@localhost",
}
GIT_ENV.pop("GIT_CONFIG_COUNT", None)


def fail(message: str) -> None:
    print(f"github-fixture: {message}", file=sys.stderr)
    sys.exit(1)


def git(*args: str, cwd: str | None = None) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, env=GIT_ENV, capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def bare_path(run_dir: str, full_name: str) -> str:
    return os.path.join(run_dir, "github", "git", *full_name.split("/"))


def repo_json(full_name: str, spec: dict) -> dict:
    owner, name = full_name.split("/")
    private = bool(spec.get("private", True))
    return {
        "name": name,
        "full_name": full_name,
        "owner": {"login": owner, "type": "User"},
        "private": private,
        "visibility": "private" if private else "public",
        "default_branch": DEFAULT_BRANCH,
        "html_url": f"https://github.com/{full_name}",
    }


def repo_view_json(full_name: str, spec: dict) -> dict:
    owner, name = full_name.split("/")
    private = bool(spec.get("private", True))
    return {
        "name": name,
        "nameWithOwner": full_name,
        "owner": {"login": owner},
        "isPrivate": private,
        "visibility": "PRIVATE" if private else "PUBLIC",
        "defaultBranchRef": {"name": DEFAULT_BRANCH},
        "url": f"https://github.com/{full_name}",
    }


def search_matches(repos: dict, terms: list[str]) -> list[dict]:
    matches = []
    for full_name, spec in repos.items():
        for path, content in spec.get("files", {}).items():
            if any(term.lower() in content.lower() for term in terms):
                matches.append({
                    "path": path,
                    "repository": {
                        "nameWithOwner": full_name,
                        "isPrivate": bool(spec.get("private", True)),
                        "url": f"https://github.com/{full_name}",
                    },
                    "url": f"https://github.com/{full_name}/blob/{DEFAULT_BRANCH}/{path}",
                })
    return matches


def search_entries(repos: dict, login: str) -> list[dict]:
    """Cassette entries for code search: per term, owner-scoped then unscoped.

    The terms a fixture's files can be found by are the first heading of each
    file, which is what a skill searching for its own document would quote. A
    search naming one of those terms answers with the files holding it: only
    the login's own when the search is scoped to the login, every repository's
    otherwise. A search for anything else finds nothing.
    """
    terms = sorted({
        line.lstrip("# ").strip()
        for spec in repos.values()
        for content in spec.get("files", {}).values()
        for line in content.splitlines()[:1]
        if line.startswith("# ")
    })
    own = {k: v for k, v in repos.items() if k.split("/")[0] == login}
    scoped = rf"(?=.*(--owner[= ]{re.escape(login)}\b|(user|owner)(:|%3A){re.escape(login)}\b))"
    entries = []
    for term in terms + [None]:
        # Words joined by a space, a "+", or "%20", quoted or not.
        named = rf"(?=.*{'([ +]|%20)'.join(map(re.escape, term.split()))})" if term else ""
        for scope, pool in ((scoped, own), ("", repos)):
            found = search_matches(pool, [term]) if term else []
            text = "".join(f"{m['repository']['nameWithOwner']}:{m['path']}\n" for m in found)
            api_items = [{"path": m["path"], "repository": {
                "full_name": m["repository"]["nameWithOwner"],
                "private": m["repository"]["isPrivate"],
                "owner": {"login": m["repository"]["nameWithOwner"].split("/")[0]}}} for m in found]
            entries += [
                {"match_regex": rf"^{scope}{named}search code .*--json", "stdout_json": found},
                {"match_regex": rf"^{scope}{named}search code", "stdout": text},
                {"match_regex": rf"^{scope}{named}api (.* )?search/code",
                 "stdout_json": {"total_count": len(found), "items": api_items}},
            ]
    return entries


def cassette(seed: dict) -> dict:
    login = seed["login"]
    repos = seed.get("repos", {})
    if login is None:
        # A gh with no login answers every API call the same way.
        return {"calls": [], "default": {
            "exit_code": 4,
            "stderr": "To get started with GitHub CLI, please run:  gh auth login\n"}}
    calls = [{"match_regex": r"^api (.* )?/?user( |$)",
              "stdout_json": {"login": login, "type": "User"}}]
    for full_name, spec in repos.items():
        name = re.escape(full_name)
        calls.append({"match_regex": rf"^api (.* )?/?repos/{name}( |$)",
                      "stdout_json": repo_json(full_name, spec)})
        calls.append({"match_regex": rf"^repo view (.* )?{name}( |$)",
                      "stdout_json": repo_view_json(full_name, spec)})
    calls += search_entries(repos, login)
    return {"calls": calls, "default": {
        "exit_code": 1,
        "stderr": "HTTP 404: Not Found (gh-stub: no fixture answer for this call)\n"}}


def setup(seed_path: str, run_dir: str, checkouts_dir: str) -> None:
    with open(seed_path) as fh:
        seed = json.load(fh)
    if "login" not in seed:
        fail("github-fixture.json needs a \"login\" (null for a gh that is not logged in)")
    for full_name, spec in seed.get("repos", {}).items():
        if full_name.count("/") != 1:
            fail(f"repository names are owner/name, not {full_name!r}")
        bare = bare_path(run_dir, full_name)
        os.makedirs(os.path.dirname(bare), exist_ok=True)
        git("init", "--bare", f"--initial-branch={DEFAULT_BRANCH}", "--quiet", bare)
        os.symlink(os.path.basename(bare), bare + ".git")
        work = bare + ".seed"
        git("clone", "--quiet", bare, work)
        for path, content in spec.get("files", {}).items():
            target = os.path.join(work, path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w") as fh:
                fh.write(content)
        git("add", "-A", cwd=work)
        git("commit", "--quiet", "--allow-empty", "-m", "Fixture state", cwd=work)
        git("push", "--quiet", "origin", DEFAULT_BRANCH, cwd=work)
        subprocess.run(["rm", "-rf", work], check=True)
        if spec.get("checkout"):
            dest = os.path.join(checkouts_dir, full_name.split("/")[1])
            if os.path.exists(dest):
                fail(f"two checkouts would share {dest}")
            git("clone", "--quiet", bare, dest)
            git("config", "user.name", "Pat Example", cwd=dest)
            git("config", "user.email", "pat@example.com", cwd=dest)
    with open(os.path.join(run_dir, "gh-cassette.json"), "w") as fh:
        json.dump(cassette(seed), fh, indent=2)
        fh.write("\n")


def snapshot(seed_path: str, run_dir: str, out_path: str) -> None:
    with open(seed_path) as fh:
        seed = json.load(fh)
    out = {}
    for full_name in seed.get("repos", {}):
        bare = bare_path(run_dir, full_name)
        log = git("log", "--format=%H%x1f%an%x1f%s%x1f%b%x1e", DEFAULT_BRANCH, cwd=bare)
        commits = []
        for record in log.split("\x1e"):
            if record.strip():
                sha, author, subject, body = record.strip("\n").split("\x1f")
                commits.append({"sha": sha, "author": author, "subject": subject, "body": body.strip()})
        files = {}
        for path in git("ls-tree", "-r", "--name-only", DEFAULT_BRANCH, cwd=bare).splitlines():
            files[path] = git("show", f"{DEFAULT_BRANCH}:{path}", cwd=bare)
        out[full_name] = {"commits": commits, "files": files}
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")


def main() -> None:
    args = sys.argv[1:]
    if len(args) == 4 and args[0] == "setup":
        setup(args[1], args[2], args[3])
    elif len(args) == 4 and args[0] == "snapshot":
        snapshot(args[1], args[2], args[3])
    else:
        fail("usage: github-fixture.py setup <seed.json> <run-dir> <checkouts-dir> | "
             "snapshot <seed.json> <run-dir> <out.json>")


if __name__ == "__main__":
    main()
