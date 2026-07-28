"""Alerting helpers."""


def send_alert(message: str) -> bool:
    if not message:
        return False
    print(f"ALERT: {message}")
    return True
