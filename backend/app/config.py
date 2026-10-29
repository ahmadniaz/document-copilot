"""Process configuration. Import `settings`; do not read the environment elsewhere."""

import os
from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Resolved from this file so Alembic, uvicorn, and tests find backend/.env
# regardless of the process working directory.
_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str = Field(min_length=1)
    supabase_anon_key: str = Field(min_length=1)
    supabase_service_role_key: str = Field(min_length=1)
    database_url: str = Field(min_length=1)
    openai_api_key: str = Field(min_length=1)
    openai_embedding_model: str = Field(min_length=1)
    openai_embedding_dimensions: int = Field(gt=0)
    allowed_origins: Annotated[list[str], NoDecode]

    @field_validator(
        "supabase_url",
        "supabase_anon_key",
        "supabase_service_role_key",
        "database_url",
        "openai_api_key",
        "openai_embedding_model",
        mode="before",
    )
    @classmethod
    def strip_required_strings(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("supabase_url")
    @classmethod
    def supabase_url_is_http(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("SUPABASE_URL must be an absolute http(s) URL")
        return value

    @field_validator("database_url")
    @classmethod
    def database_url_is_postgres(cls, value: str) -> str:
        if urlsplit(value).scheme not in {"postgres", "postgresql"}:
            raise ValueError("DATABASE_URL must be a postgresql URL")
        return value

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            raw_items = value.split(",")
        elif isinstance(value, list):
            raw_items = value
        else:
            raise TypeError("ALLOWED_ORIGINS must be a comma-separated list of origins")
        origins = [str(item).strip() for item in raw_items if str(item).strip()]
        if not origins:
            raise ValueError("ALLOWED_ORIGINS must include at least one origin")
        return origins


def _mirror_openai_api_key(api_key: str) -> None:
    # The OpenAI SDK reads OPENAI_API_KEY from the process environment when a
    # client is constructed without an explicit key. pydantic-settings loads
    # .env into this object only, so the key has to be copied across here.
    os.environ["OPENAI_API_KEY"] = api_key


settings = Settings()
_mirror_openai_api_key(settings.openai_api_key)
