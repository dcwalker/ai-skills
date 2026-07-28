"""Application bootstrap module. Runs once at process startup."""

from app import plugins
from app.plugin_registry import registry


def start():
    print(f"Loaded {len(registry)} plugins")
