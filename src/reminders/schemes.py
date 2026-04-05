from datetime import datetime

from pydantic import BaseModel

from src.reminders.enums import EventRepeatInterval


class EventCreateScheme(BaseModel):
    description: str
    event_datetime: datetime
    repeat_interval: EventRepeatInterval | None
    message_count: int | None = None


class EventScheme(BaseModel):
    id: int
    user_id: int
    description: str
    event_datetime: datetime
    repeat_interval: EventRepeatInterval | None
    message_count: int

    class Config:
        from_attributes = True