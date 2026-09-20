#!/usr/bin/env python3

"""Shim: forwards to the real script bundled with the resolve-sonarqube-issues skill.

Claude Code appends <plugin-root>/bin to PATH for every installed plugin, so
this shim is what makes the plain 'list-sonar-issues.py' invocation work. The
real script stays under skills/ so each skill's bundled resources remain
together.

The plugin root is resolved relative to this file rather than hard-coded: the
install path contains a commit hash that changes on every plugin update.
"""

import os
import runpy
import sys

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
TARGET = os.path.join(
    PLUGIN_ROOT, "skills", "resolve-sonarqube-issues", "scripts", "list-sonar-issues.py"
)

if not os.path.isfile(TARGET):
    sys.exit(f"Error: could not find {TARGET}")

# Run the real script inside this process rather than spawning an interpreter.
# Forwarding argv into a new process makes a pass-through shim a command-argument
# sink, and there is nothing here that could validate its way out of that: every
# argument legitimately belongs to the target's own parser, so filtering any of
# them would just break callers. runpy keeps them as data -- a sys.argv list,
# never a command line -- and the target's own sys.exit still sets this
# process's exit status.
sys.argv = [TARGET, *sys.argv[1:]]
runpy.run_path(TARGET, run_name="__main__")
