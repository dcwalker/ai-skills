"""Inventory helpers."""


def restock_needed(current_qty: int, threshold: int) -> bool:
    return current_qty < threshold


def days_of_supply(current_qty: int, daily_usage: float) -> float:
    if daily_usage <= 0:
        return float("inf")
    return current_qty / daily_usage
