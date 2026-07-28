"""Simple decorator-based plugin registry."""

registry = {}


def register(name):
    def decorator(fn):
        registry[name] = fn
        return fn
    return decorator
