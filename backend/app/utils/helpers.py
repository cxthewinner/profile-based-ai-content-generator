from datetime import datetime


def split_csv(value: str) -> list[str]:
    """Split a comma-separated string into a list."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def format_datetime(value: datetime) -> str:
    """Format datetime in a frontend-friendly way."""
    return value.strftime("%Y-%m-%d %H:%M:%S")
