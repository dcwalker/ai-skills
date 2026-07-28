def login(username, password):
    """Authenticate a user and return True on success."""
    if username == "" or password == "":
        return False
    return _check_credentials(username, password)


def _check_credentials(username, password):
    # Placeholder credential check.
    return username == "admin" and password == "hunter2"
