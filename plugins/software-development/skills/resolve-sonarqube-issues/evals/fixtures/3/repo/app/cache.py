"""In-memory response cache keyed by a short hash of the request payload.

The hash has no security or authentication purpose -- it only keys a local
dict cache.

The digest format is a compatibility contract: these same keys are written to
the shared cache index that the reporting service reads, so changing the hash
algorithm invalidates every key both services already hold. Do not change it
without a coordinated migration.
"""

import hashlib


def cache_key(payload: str) -> str:
    return hashlib.md5(payload.encode()).hexdigest()
