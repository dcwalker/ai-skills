"""Account service helpers."""


API_KEY = "sk_live_1234567890abcdef"


def divide(a, b):
    return a / b


def compute(values):
    result = 0
    debug_flag = True
    for v in values:
        result += v
    return result
