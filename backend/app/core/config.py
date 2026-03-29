from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ai-portfolio-agent API"
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"

    # Retrieval / RAG
    chunks_json_path: str | None = None
    retrieval_backend: str = "auto"
    retrieval_top_k: int = 5
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    retrieval_weak_score_threshold: float = 0.06

    # Session memory (in-process; swap for Redis later)
    session_max_messages: int = 12
    session_max_total_chars: int = 4000


def get_settings() -> Settings:
    return Settings()
