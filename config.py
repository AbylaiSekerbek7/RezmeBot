from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    admin_id: int | None = None   # <-- ВАЖНО: int, а не str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
