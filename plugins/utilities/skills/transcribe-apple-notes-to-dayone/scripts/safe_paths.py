"""Path containment shared by the transcribe-apple-notes-to-dayone scripts.

Paths given on the command line must lie under the user's home directory or
$TMPDIR (where mktemp creates files), so a mistyped or hostile argument
cannot read or write elsewhere.
"""

import os
import sys
import tempfile


def allowed_roots():
    """Where the scripts may read or write: the user's home and $TMPDIR."""
    roots = {os.path.expanduser("~"), tempfile.gettempdir()}
    return sorted({os.path.realpath(root) for root in roots if os.path.isdir(root)})


def contained_path(path, name):
    """Resolve path, exiting with an error if it is outside the allowed roots."""
    resolved = os.path.realpath(os.path.expanduser(path))
    for root in allowed_roots():
        if resolved == root or resolved.startswith(root + os.sep):
            return resolved
    sys.exit(
        f"{name} must be inside your home directory or {tempfile.gettempdir()}; "
        f"got {path!r}. Create working folders with mktemp -d."
    )
