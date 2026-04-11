from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseModel):
    token: str
    reminder_token: str


class DatabaseSettings(BaseModel):
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str = "5432"
    postgres_db: str
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> str:
        return "postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}".format_map(
            self.model_dump()
        )


class EmailSettings(BaseModel):
    host: str = "smtp.gmail.com"
    port: int = 465
    username: str = ""
    password: str = ""
    from_address: str = ""
    use_tls: bool = True


class JWTSettings(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30


class Settings(BaseSettings):
    bot: BotSettings
    database: DatabaseSettings
    email: EmailSettings = EmailSettings()
    jwt: JWTSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
