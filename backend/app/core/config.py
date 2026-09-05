from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Email Threat Detection Platform"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://emailsec:emailsec@localhost:5432/email_security"
    storage_root: Path = Path("./data")
    max_email_size_mb: int = 25
    cors_origins: list[str] = ["http://localhost:5173"]
    GMAIL_CREDENTIALS_PATH: str = "./secrets/gmail_credentials.json"
    GMAIL_TOKEN_PATH: str = "./data/oauth/gmail_token.json"
    VIRUSTOTAL_API_KEY: str | None = None
    GOOGLE_SAFE_BROWSING_API_KEY: str | None = None
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def max_email_size_bytes(self) -> int:
        return self.max_email_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
