from typing import Optional

from sqlalchemy import select

from src.database import User
from src.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями."""

    def __init__(self, session):
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(self.model).where(self.model.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

