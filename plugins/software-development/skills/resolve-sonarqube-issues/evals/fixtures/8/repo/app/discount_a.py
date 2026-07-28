"""Discount calculation used at checkout."""


def apply_discount_a(price, pct):
    if pct < 0 or pct > 100:
        raise ValueError("pct must be between 0 and 100")
    return round(price * (1 - pct / 100), 2)
