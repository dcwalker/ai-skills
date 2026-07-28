"""In-house table renderer. Predates the vendored formatter; kept separate
because it has diverged behavior planned (colspan support incoming)."""


def render_row(cells):
    padded = [str(c).ljust(12) for c in cells]
    return " | ".join(padded)
