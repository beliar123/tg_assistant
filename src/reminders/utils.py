import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from src.reminders.schemes import EventScheme
from src.templates.renderer import render

logger = logging.getLogger(__name__)

MSK = ZoneInfo("Europe/Moscow")
UTC = ZoneInfo("UTC")


def parse_date_time(date_time_str: str) -> datetime | None:
    """Парсит строку как московское время и конвертирует в UTC."""
    try:
        naive = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        msk_dt = naive.replace(tzinfo=MSK)
        return msk_dt.astimezone(UTC)
    except ValueError:
        return None


def to_msk(dt: datetime) -> str:
    """Конвертирует UTC datetime в строку московского времени."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(MSK).strftime("%Y-%m-%d %H:%M")


def validate_date_time(date_time_str: str) -> bool:
    return parse_date_time(date_time_str) is not None
