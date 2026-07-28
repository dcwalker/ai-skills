"""In-memory response cache keyed by a short hash of the request payload.

This hash is used only to key a local dict cache -- it has no security or
authentication purpose.
"""

import hashlib


def cache_key(payload: str) -> str:
    return hashlib.md5(payload.encode()).hexdigest()
