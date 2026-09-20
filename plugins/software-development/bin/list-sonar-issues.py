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
import sys

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
TARGET = os.path.join(
    PLUGIN_ROOT, "skills", "resolve-sonarqube-issues", "scripts", "list-sonar-issues.py"
)

if not os.path.isfile(TARGET):
    sys.exit(f"Error: could not find {TARGET}")

os.execv(sys.executable, [sys.executable, TARGET] + sys.argv[1:])
