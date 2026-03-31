import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from src.configs import settings
from src.templates.renderer import render

logger = logging.getLogger(__name__)


async def send_email_reminder(to_address: str, description: str, event_id: int) -> bool:
    """Отправляет напоминание на email. Возвращает True если успешно."""
    if not to_address:
        return False

    cfg = settings.email
    if not cfg.username or not cfg.password or not cfg.from_address:
        logger.warning("Email не настроен — пропускаю отправку.")
        return False

    try:
        body_html = render("reminder_email.html", description=description)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔔 Напоминание: {description[:50]}"
        msg["From"] = cfg.from_address
        msg["To"] = to_address
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        await aiosmtplib.send(
            msg,
            hostname=cfg.host,
            port=cfg.port,
            username=cfg.username,
            password=cfg.password,
            use_tls=cfg.use_tls,
        )
        logger.info(f"Email-напоминание id:{event_id} отправлено на {to_address}")
        return True
    except Exception as e:
        logger.error(
            f"Ошибка при отправке email-напоминания id:{event_id} на {to_address}: {e}"
        )
        return False
