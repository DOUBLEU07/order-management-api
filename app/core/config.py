from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Order Management API"
    DATABASE_URL: str
    REDIS_URL: str

    PRODUCT_CACHE_TTL_SECONDS: int = 60


settings = Settings()
