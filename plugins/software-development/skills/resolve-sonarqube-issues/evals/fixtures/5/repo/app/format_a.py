"""Currency formatting used by the receipts module."""


def format_currency(amount):
    dollars = int(amount)
    cents = round((amount - dollars) * 100)
    return f"${dollars}.{cents:02d}"
