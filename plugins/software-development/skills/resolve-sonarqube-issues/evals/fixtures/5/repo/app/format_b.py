"""Currency formatting used by the invoices module."""


def format_price(amount):
    dollars = int(amount)
    cents = round((amount - dollars) * 100)
    return f"${dollars}.{cents:02d}"
