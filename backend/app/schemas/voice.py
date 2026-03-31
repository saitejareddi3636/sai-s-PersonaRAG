from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.chat import AudioMetadata, RetrievalHitSchema, SourceCitation


class VoiceChatResponse(BaseModel):
    transcript: str = Field(..., description="Transcribed user speech")
    answer: str = Field(..., description="Grounded assistant response")
    confidence: Literal["high", "medium", "low"] = Field(
        ..., description="Confidence from RAG-backed answer"
    )
    grounding_note: str | None = Field(None, description="Note about grounding quality")
    sources: list[SourceCitation] = Field(default_factory=list)
    session_id: str | None = Field(default=None)
    audio: AudioMetadata | None = Field(default=None)
    tts_error: str | None = Field(default=None)
    retrieval: list[RetrievalHitSchema] = Field(default_factory=list)
    retrieval_error: str | None = Field(default=None)
    stt_provider: str = Field(default="faster-whisper")
    stt_language: str | None = Field(default=None)
