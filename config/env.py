from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseSettings):
    """Runtime config from the environment. Fill `.env` before Neon / OpenAI phases."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False,
        populate_by_name=True,
    )

    secret_key: str = Field(
        default='django-insecure-change-me-before-production',
        alias='SECRET_KEY',
    )
    debug: bool = Field(default=True, alias='DEBUG')
    allowed_hosts: str = Field(default='localhost,127.0.0.1', alias='ALLOWED_HOSTS')

    database_url: str | None = Field(default=None, alias='DATABASE_URL')

    openai_api_key: str = Field(default='', alias='OPENAI_API_KEY')
    openai_embedding_model: str = Field(default='text-embedding-3-small', alias='OPENAI_EMBEDDING_MODEL')
    openai_chat_model: str = Field(default='gpt-4o-mini', alias='OPENAI_CHAT_MODEL')

    rag_chunk_tokens: int = Field(default=700, alias='RAG_CHUNK_TOKENS')
    rag_chunk_overlap: float = Field(default=0.15, alias='RAG_CHUNK_OVERLAP')
    rag_top_k: int = Field(default=5, alias='RAG_TOP_K')
    rag_min_similarity: float = Field(default=0.25, alias='RAG_MIN_SIMILARITY')

    max_upload_mb: int = Field(default=10, alias='MAX_UPLOAD_MB')
    default_theme: str = Field(default='light', alias='DEFAULT_THEME')

    @field_validator('database_url', mode='before')
    @classmethod
    def empty_url_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(',') if host.strip()]

    @property
    def is_postgres(self) -> bool:
        url = (self.database_url or '').lower()
        return url.startswith('postgres')

    @property
    def openai_configured(self) -> bool:
        return bool(self.openai_api_key.strip())


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
