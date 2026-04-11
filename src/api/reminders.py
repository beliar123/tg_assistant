from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user, get_uow
from src.core.unitofwork import UnitOfWork
from src.database.models import Event, User
from src.reminders.schemes import EventCreateScheme, EventScheme

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/", response_model=list[EventScheme])
async def list_reminders(
    current_user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    events = await uow.event.get_all_by_user_id(current_user.id)
    return [EventScheme.model_validate(e) for e in events]


@router.get("/{event_id}", response_model=EventScheme)
async def get_reminder(
    event_id: int,
    current_user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    event = await uow.event.get_by_id(event_id)
    if not event or event.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Напоминание не найдено")
    return EventScheme.model_validate(event)


@router.post("/", response_model=EventScheme, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    data: EventCreateScheme,
    current_user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    new_event = Event(
        user_id=current_user.id,
        description=data.description,
        event_datetime=data.event_datetime,
        repeat_interval=data.repeat_interval,
        message_count=data.message_count if data.message_count is not None else 3,
    )
    event = await uow.event.add(new_event)
    await uow.commit()
    await uow.session.refresh(event)
    return EventScheme.model_validate(event)


@router.put("/{event_id}", response_model=EventScheme)
async def update_reminder(
    event_id: int,
    data: EventCreateScheme,
    current_user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    event = await uow.event.get_by_id(event_id)
    if not event or event.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Напоминание не найдено")
    updated = await uow.event.update(event_id, data.model_dump(exclude_unset=True))
    await uow.commit()
    return EventScheme.model_validate(updated)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    event_id: int,
    current_user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    event = await uow.event.get_by_id(event_id)
    if not event or event.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Напоминание не найдено")
    await uow.event.delete(event_id)
    await uow.commit()
