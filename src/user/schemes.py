from pydantic import BaseModel, EmailStr


class UserCreateScheme(BaseModel):
    telegram_id: int
    chat_id: int
    name: str
    lastname: str | None = None
    email: str | None = None


class UserUpdateScheme(BaseModel):
    name: str | None = None
    lastname: str | None = None
    email: str | None = None
    is_active: bool | None = None


class UserScheme(BaseModel):
    id: int
    telegram_id: int
    chat_id: int
    name: str
    lastname: str | None
    email: str | None
    is_active: bool

    class Config:
        from_attributes = True
