from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ai-portfolio-agent API"
    # Browsers treat localhost and 127.0.0.1 as different origins — list both for local dev.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    log_level: str = "INFO"

    # Retrieval / RAG
    chunks_json_path: str | None = None
    retrieval_backend: str = "tfidf"
    retrieval_top_k: int = 3
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2:3b"
    ollama_embed_model: str = "nomic-embed-text"
    retrieval_weak_score_threshold: float = 0.06

    # Session memory (in-process; swap for Redis later)
    session_max_messages: int = 12
    session_max_total_chars: int = 4000

    # TTS (Text-to-Speech)
    # mock | local-service | clean-xtts | f5-tts
    tts_provider: str = "mock"
    tts_service_url: str = "http://localhost:9000"  # local-service (e.g. legacy F5-style API)
    clean_tts_url: str = "http://127.0.0.1:8010"  # clean-tts FastAPI (XTTS POST /tts)


def get_settings() -> Settings:
    return Settings()
