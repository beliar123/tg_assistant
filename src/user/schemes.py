from pydantic import BaseModel


class UserUpdateScheme(BaseModel):
    name: str | None = None
    lastname: str | None = None
    email: str | None = None


class UserScheme(BaseModel):
    id: int
    username: str
    name: str
    lastname: str | None
    email: str | None
    is_active: bool

    class Config:
        from_attributes = True
