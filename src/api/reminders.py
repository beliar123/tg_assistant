from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_uow
from src.core.unitofwork import UnitOfWork
from src.database.models import Event
from src.reminders.schemes import EventCreateScheme, EventScheme

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/{user_id}", response_model=list[EventScheme])
async def list_reminders(user_id: int, uow: UnitOfWork = Depends(get_uow)):
    events = await uow.event.get_all_by_user_id(user_id)
    return [EventScheme.model_validate(e) for e in events]


@router.get("/{user_id}/{event_id}", response_model=EventScheme)
async def get_reminder(user_id: int, event_id: int, uow: UnitOfWork = Depends(get_uow)):
    event = await uow.event.get_by_id(event_id)
    if not event or event.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Напоминание не найдено")
    return EventScheme.model_validate(event)


@router.post("/{user_id}", response_model=EventScheme, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    user_id: int, data: EventCreateScheme, uow: UnitOfWork = Depends(get_uow)
):
    new_event = Event(
        user_id=user_id,
        description=data.description,
        event_datetime=data.event_datetime,
        repeat_interval=data.repeat_interval,
        message_count=data.message_count if data.message_count is not None else 3,
    )
    event = await uow.event.add(new_event)
    await uow.commit()
    return EventScheme.model_validate(event)


@router.put("/{user_id}/{event_id}", response_model=EventScheme)
async def update_reminder(
    user_id: int,
    event_id: int,
    data: EventCreateScheme,
    uow: UnitOfWork = Depends(get_uow),
):
    event = await uow.event.get_by_id(event_id)
    if not event or event.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Напоминание не найдено")
    updated = await uow.event.update(event_id, data.model_dump(exclude_unset=True))
    await uow.commit()
    return EventScheme.model_validate(updated)


@router.delete("/{user_id}/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(user_id: int, event_id: int, uow: UnitOfWork = Depends(get_uow)):
    event = await uow.event.get_by_id(event_id)
    if not event or event.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Напоминание не найдено")
    await uow.event.delete(event_id)
    await uow.commit()
