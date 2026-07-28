"""Legacy CSV export helper."""

import hashlib


def export_checksum(payload: str) -> str:
    """Return a short checksum for detecting accidental re-exports.
    Not used for authentication or any security-sensitive purpose."""
    return hashlib.md5(payload.encode()).hexdigest()
