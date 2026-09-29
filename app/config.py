from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    secret_key: str = "development-only-change-me"
    database_path: str = "./pocketsmart.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    access_token_minutes: int = 720
    max_image_mb: int = 5
    cors_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
