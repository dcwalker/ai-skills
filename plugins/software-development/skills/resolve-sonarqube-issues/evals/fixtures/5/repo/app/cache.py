"""Password-reset token helper."""

import hashlib


def reset_token(user_id: str, secret: str) -> str:
    """Generate a password-reset token for the given user."""
    return hashlib.md5(f"{user_id}:{secret}".encode()).hexdigest()
