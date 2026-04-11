import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from arq.connections import ArqRedis

from src.core.unitofwork import get_uow
from src.notifications.email import send_email_reminder
from src.scheduler.utils import calculate_next_occurrence

logger = logging.getLogger(__name__)


async def send_reminder(
    context: dict[str, Any],
    event_id: int,
    message: str,
    user_email: str | None = None,
):
    logger.info("Отправка напоминания %i", event_id)
    if user_email:
        await send_email_reminder(user_email, message, event_id)


async def check_events(context: dict[str, Any]):
    try:
        logger.info("Получение напоминаний.")
        now = datetime.now(tz=UTC)
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        redis: ArqRedis = context["redis"]

        async with get_uow() as uow:
            events = await uow.event.get_events_by_datetime(period_start, period_end)
            logger.info(f"Полученно {len(events)} напоминаний.")
            for event in events:
                user = await uow.user.get_by_id(event.user_id)
                for count in range(event.message_count):
                    time_to_send = (
                        event.event_datetime + timedelta(hours=count, minutes=30)
                        if count != 0
                        else event.event_datetime
                    )
                    await redis.enqueue_job(
                        "send_reminder",
                        event.id,
                        event.description,
                        user.email if user else None,
                        _job_id=f"reminder_{event.id}_{count}",
                        _defer_until=time_to_send,
                    )
                    logger.info(
                        "Напоминание id: %d поставлено в очередь на отправку %s в %s.",
                        event.id, time_to_send.date(), time_to_send.time(),
                    )

                if event.repeat_interval is None:
                    await uow.event.delete(event.id)
                else:
                    next_occurrence = calculate_next_occurrence(
                        event.event_datetime, event.repeat_interval
                    )
                    await uow.event.update(event.id, {"event_datetime": next_occurrence})

            await uow.commit()

    except Exception as e:
        logger.error(f"Ошибка при проверке событий: {e}")
