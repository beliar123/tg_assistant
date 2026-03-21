from src.core.unitofwork import get_uow
from src.database.models import User


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
