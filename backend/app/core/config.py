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
    # Keeps the chat model loaded between requests (faster after first turn on a small VM).
    # Set OLLAMA_KEEP_ALIVE=0 to unload immediately after each call.
    ollama_keep_alive: str = "15m"
    # CPU latency: cap generation and context (Ollama /api/chat "options"). None = omit (Ollama defaults).
    ollama_num_predict: int | None = 384
    ollama_num_ctx: int | None = 2048
    retrieval_weak_score_threshold: float = 0.06
    # Truncate each retrieved chunk in the LLM prompt (smaller prompt = faster on CPU).
    retrieval_max_chars_per_chunk: int = 1200

    # Session memory (in-process; swap for Redis later)
    session_max_messages: int = 12
    session_max_total_chars: int = 4000

    # STT (Speech-to-Text)
    stt_provider: str = "faster-whisper"
    stt_model_size: str = "base"  # tiny, base, small, medium, large (base = good speed/accuracy for Mac CPU)
    stt_device: str = "cpu"  # cpu | cuda
    stt_compute_type: str = "int8"  # int8 (fastest on CPU), int16, float16, float32
    stt_beam_size: int = 1  # 1=greedy (fastest), >1 uses beam search (slower)
    stt_timeout_s: float = 60.0  # Reserved for future timeout implementation (not currently used)
    stt_language: str | None = None  # Optional: 'en', 'es', 'fr', etc. — skips lang detection = faster CPU path
    # Skip timestamp tokens in the decoder (faster; can slightly change wording vs timestamps on).
    stt_without_timestamps: bool = True
    # Load Whisper weights at API startup so the first voice request is not paying model load.
    stt_warmup_on_startup: bool = True
    # Faster-Whisper Silero VAD (reduces silence / noise hallucinations at decode time; not live endpointing).
    stt_vad_filter: bool = True
    stt_vad_min_silence_duration_ms: int = 550
    # Slightly lower = less extra audio around speech segments (smaller decode work).
    stt_vad_speech_pad_ms: int = 320

    # TTS (Text-to-Speech)
    # Provider: piper (default, reliable, local CPU) | mock (silent test) | local-service | f5-tts (disabled)
    tts_provider: str = "piper"
    tts_service_url: str = "http://localhost:9000"  # Only for local-service provider
    # Piper TTS (default, runs locally on CPU)
    piper_binary: str = "piper"  # Binary command or absolute path
    piper_model_path: str = ""  # Absolute path to .onnx model file (required for piper provider)
    piper_speaker_id: int | None = None  # 0, 1, 2, etc. for multi-speaker models; None for single-speaker
    piper_timeout_s: float = 45.0  # Max seconds per synthesis request
    voice_tts_max_chars: int = 420  # Voice-mode spoken summary cap to reduce TTS latency


def get_settings() -> Settings:
    return Settings()
