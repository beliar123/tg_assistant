import logging
from typing import Any

from telegram import Bot

from src.templates.renderer import render

logger = logging.getLogger(__name__)


async def send_telegram_reminder(
    context: dict[str, Any],
    user_tg_id: int,
    description: str,
    event_id: int,
) -> bool:
    """Отправляет напоминание в Telegram. Возвращает True если успешно."""
    bot: Bot = context["bot"]
    try:
        text = render("reminder_fire.md", description=description)
        await bot.send_message(user_tg_id, text=text, parse_mode="MarkdownV2")
        logger.info(f"Напоминание id:{event_id} отправлено в Telegram пользователю(telegram_id: {user_tg_id})")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке Telegram-напоминания id:{event_id}: {e}")
        return False