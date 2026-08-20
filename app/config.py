from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    app_url: str = "http://localhost:5173"
    trusted_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    default_openai_model: str = "gpt-5-mini"
    allowed_openai_models: str = "gpt-5-mini,gpt-5.2"
    request_timeout_seconds: float = 60.0
    max_output_tokens: int = 1200
    requests_per_hour: int = 30
    api_docs_enabled: bool = True

    @property
    def origins(self) -> list[str]:
        return [value.strip().rstrip("/") for value in self.trusted_origins.split(",") if value.strip()]

    @property
    def models(self) -> set[str]:
        return {value.strip() for value in self.allowed_openai_models.split(",") if value.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
