import logging
from datetime import datetime

from src.core.unitofwork import get_uow
from src.database.models import Event
from src.reminders.schemes import EventCreateScheme, EventRepeatInterval, EventScheme

logger = logging.getLogger(__name__)


async def add_event(event: EventCreateScheme, user_id: int) -> EventScheme:
    async with get_uow() as uow:
        new_event = Event(
            user_id=user_id,
            description=event.description,
            event_datetime=event.event_datetime,
            repeat_interval=event.repeat_interval,
            message_count=event.message_count,
        )
        new_event = await uow.event.add(new_event)
        await uow.commit()
        return EventScheme.model_validate(new_event)


async def get_all_events(user_tg_id: int) -> tuple[EventScheme, ...]:
    try:
        async with get_uow() as uow:
            events = await uow.event.get_all_by_user_tg(user_tg_id)
            return tuple(EventScheme.model_validate(event) for event in events)
    except Exception as e:
        logger.error(f"Ошибка при получении событий: {e}")
        return ()


async def delete_event(event_id: int, user_tg_id: int) -> bool:
    async with get_uow() as uow:
        user = await uow.user.get_user_by_tg_id(user_tg_id)
        event = await uow.event.get_by_id(event_id)
        if user and event and event.user_id == user.id:
            await uow.session.delete(event)
            await uow.commit()
            return True
        return False


async def update_event(
    event_id: str,
    description: str,
    event_datetime: datetime,
    repeat_interval: EventRepeatInterval | None,
) -> EventScheme | None:
    async with get_uow() as uow:
        result = await uow.event.update(
            int(event_id),
            EventCreateScheme(
                description=description,
                event_datetime=event_datetime,
                repeat_interval=repeat_interval,
            ).model_dump(exclude_unset=True),
        )
        await uow.commit()
        return EventScheme.model_validate(result)
