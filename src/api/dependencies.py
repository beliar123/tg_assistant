from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import decode_token
from src.core.unitofwork import UnitOfWork
from src.database import db_helper
from src.database.models import User

bearer_scheme = HTTPBearer()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_helper.session_factory() as session:
        yield session


async def get_uow(session: AsyncSession = Depends(get_session)) -> UnitOfWork:
    return UnitOfWork(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    uow: UnitOfWork = Depends(get_uow),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_token(credentials.credentials, expected_type="access")
    except JWTError:
        raise credentials_exception

    user = await uow.user.get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    return user
