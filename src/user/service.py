import re

from src.core.unitofwork import get_uow
from src.database.models import User

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    return bool(_EMAIL_RE.match(email))


async def get_or_create_user(
    telegram_id: int,
    chat_id: int,
    firstname: str,
    lastname: str | None,
) -> int:
    """Возвращает внутренний user.id, создаёт пользователя если не существует."""
    async with get_uow() as uow:
        user = User(
            telegram_id=telegram_id,
            chat_id=chat_id,
            name=firstname,
            lastname=lastname,
        )
        user = await uow.user.get_or_create_user_by_tg_id(user)
        await uow.commit()
    return user.id


async def set_user_email(telegram_id: int, email: str) -> bool:
    """Сохраняет email пользователя. Возвращает True если успешно."""
    async with get_uow() as uow:
        user = await uow.user.get_user_by_tg_id(telegram_id)
        if not user:
            return False
        await uow.user.update(user.id, {"email": email})
        await uow.commit()
    return True
