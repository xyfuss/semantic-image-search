from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    database_url_unpooled: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()