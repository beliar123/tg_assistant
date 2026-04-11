from pydantic import BaseModel


class UserUpdateScheme(BaseModel):
    name: str | None = None
    lastname: str | None = None
    email: str | None = None
    is_active: bool | None = None


class UserScheme(BaseModel):
    id: int
    username: str
    telegram_id: int | None
    chat_id: int | None
    name: str
    lastname: str | None
    email: str | None
    is_active: bool

    class Config:
        from_attributes = True
