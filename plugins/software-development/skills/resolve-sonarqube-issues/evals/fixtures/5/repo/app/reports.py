"""Reporting helpers."""


def summarize(rows):
    total = 0
    row_count = 0
    for row in rows:
        total += row["amount"]
    return total
