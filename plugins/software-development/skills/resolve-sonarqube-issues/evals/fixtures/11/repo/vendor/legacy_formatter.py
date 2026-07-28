"""Vendored copy of upstream formatter v1.2. Do not modify directly;
changes should be contributed upstream and this file re-vendored. See UPSTREAM.md."""


def format_row(cells):
    padded = [str(c).ljust(12) for c in cells]
    return " | ".join(padded)
