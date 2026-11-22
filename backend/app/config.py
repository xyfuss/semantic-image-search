from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    database_url_unpooled: str | None = None
    secret_key: str
    r2_access_key: str
    r2_secret_access_key: str
    r2_endpoint_url: str
    r2_bucket: str
    redis_url: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
