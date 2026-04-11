from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.configs import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(payload, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)


def create_access_token(user_id: int) -> str:
    return _create_token(
        {"sub": str(user_id), "type": "access"},
        timedelta(minutes=settings.jwt.access_token_expire_minutes),
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        {"sub": str(user_id), "type": "refresh"},
        timedelta(days=settings.jwt.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str) -> int:
    """Декодирует токен и возвращает user_id. Raises JWTError при невалидном токене."""
    payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
    if payload.get("type") != expected_type:
        raise JWTError("Invalid token type")
    sub = payload.get("sub")
    if sub is None:
        raise JWTError("Missing subject")
    return int(sub)
