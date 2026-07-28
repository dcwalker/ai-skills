"""Cart pricing helpers."""


def calculate_total(items):
    total = 0
    unused_count = 0
    for item in items:
        total += item["price"]
    return total
