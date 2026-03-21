from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, MetaData, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func

from src.configs import settings
from src.reminders.schemes import EventRepeatInterval
from src.utils import camel_case_to_snake_case, datetime_utc_now


class BaseDbModel(DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(
        naming_convention=settings.database.naming_convention,
    )

    type_annotation_map = {dict[str, Any]: postgresql.JSONB, list[str]: postgresql.JSONB}

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime_utc_now,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime_utc_now,
        server_default=func.now(),
        onupdate=datetime.now,
    )


class User(BaseDbModel):
    telegram_id: Mapped[int] = mapped_column(unique=True)
    chat_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(String(32))
    lastname: Mapped[str | None] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(default=True)
    events: Mapped[list["Event"]] = relationship(back_populates="user")


class Event(BaseDbModel):
    event_datetime: Mapped[datetime]
    description: Mapped[str] = mapped_column(Text)
    repeat_interval: Mapped[EventRepeatInterval | None] = mapped_column(
        postgresql.ENUM(
            EventRepeatInterval,
            name="event_repeat_intervals",
        )
    )
    message_count: Mapped[int] = mapped_column(default=3)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="events")
