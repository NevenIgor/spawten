"""Validation helpers for the lead form inputs."""
import re
from datetime import date, datetime

PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


def parse_date(raw: str) -> date | None:
    """Parse DD.MM.YYYY (also accepts DD-MM-YYYY / DD/MM/YYYY)."""
    raw = raw.strip()
    normalized = re.sub(r"[/\-.]", ".", raw)
    if not re.fullmatch(r"\d{1,2}\.\d{1,2}\.\d{4}", normalized):
        return None
    try:
        return datetime.strptime(normalized, "%d.%m.%Y").date()
    except ValueError:
        return None


def format_date(value: date | None) -> str:
    return value.strftime("%d.%m.%Y") if value else ""


def validate_phone(raw: str) -> str | None:
    """Return cleaned phone string or None if invalid."""
    raw = raw.strip()
    if PHONE_RE.match(raw):
        return raw
    return None
