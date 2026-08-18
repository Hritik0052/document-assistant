from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

FREE_CHAT_ROUTER = 'openrouter/free'


def strip_env(value):
    if isinstance(value, str):
        return value.strip().strip("'").strip('"')
    return value


def is_free_openrouter_model(model: str) -> bool:
    name = model.strip()
    return name == FREE_CHAT_ROUTER or name.endswith(':free')


class AppSettings(BaseSettings):
    """Runtime config from the environment."""

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

    openrouter_api_key: str = Field(
        default='',
        validation_alias=AliasChoices('OPENROUTER_API_KEY', 'OPEN_ROUTER_API_KEY'),
    )
    openrouter_base_url: str = Field(
        default='https://openrouter.ai/api/v1',
        alias='OPENROUTER_BASE_URL',
    )
    openrouter_chat_model: str = Field(
        default=FREE_CHAT_ROUTER,
        alias='OPENROUTER_CHAT_MODEL',
    )
    openrouter_embedding_model: str = Field(
        default='nvidia/nemotron-3-embed-1b:free',
        alias='OPENROUTER_EMBEDDING_MODEL',
    )
    embedding_dimensions: int = Field(default=2048, alias='EMBEDDING_DIMENSIONS')

    rag_chunk_tokens: int = Field(default=700, alias='RAG_CHUNK_TOKENS')
    rag_chunk_overlap: float = Field(default=0.15, alias='RAG_CHUNK_OVERLAP')
    rag_top_k: int = Field(default=5, alias='RAG_TOP_K')
    rag_min_similarity: float = Field(default=0.25, alias='RAG_MIN_SIMILARITY')

    max_upload_mb: int = Field(default=10, alias='MAX_UPLOAD_MB')
    default_theme: str = Field(default='light', alias='DEFAULT_THEME')

    @field_validator('database_url', mode='before')
    @classmethod
    def clean_database_url(cls, value):
        cleaned = strip_env(value)
        if not cleaned:
            return None
        return cleaned

    @field_validator(
        'openrouter_api_key',
        'openrouter_base_url',
        'openrouter_chat_model',
        'openrouter_embedding_model',
        'secret_key',
        'allowed_hosts',
        mode='before',
    )
    @classmethod
    def clean_strings(cls, value):
        return strip_env(value) if value is not None else value

    @field_validator('openrouter_chat_model', 'openrouter_embedding_model')
    @classmethod
    def require_free_models(cls, value: str) -> str:
        if not is_free_openrouter_model(value):
            raise ValueError(
                f'{value} is not a free OpenRouter model. Use a slug ending in :free or openrouter/free.'
            )
        return value

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(',') if host.strip()]

    @property
    def is_postgres(self) -> bool:
        url = (self.database_url or '').lower()
        return url.startswith('postgres')

    @property
    def llm_configured(self) -> bool:
        return bool(self.openrouter_api_key.strip())


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
