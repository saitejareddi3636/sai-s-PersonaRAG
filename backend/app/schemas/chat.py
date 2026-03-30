from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: str | None = Field(
        default=None,
        description="Optional id to continue a short multi-turn chat; omit to start a new session.",
    )
    include_tts: bool = Field(
        default=False,
        description="Optional: if True, backend will synthesize audio for the answer (requires TTS service)",
    )


class AudioMetadata(BaseModel):
    """Optional audio metadata for synthesized answer."""

    audio_url: str | None = Field(None, description="URL to access synthesized audio")
    audio_path: str | None = Field(None, description="Internal file path (reference)")
    duration_ms: int | None = Field(None, description="Duration in milliseconds")
    provider: str = Field(..., description="TTS provider (mock, local-f5-tts, etc.)")


class RetrievalHitSchema(BaseModel):
    id: str
    score: float
    content_type: str
    source_file: str
    section_title: str
    section_level: int
    text_preview: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceCitation(BaseModel):
    """Clean citation showing where answer came from."""

    excerpt: str = Field(..., description="The actual quote/text referenced")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Grounded reply for the recruiter")
    confidence: Literal["high", "medium", "low"] = Field(
        ...,
        description="How well the retrieved context supports the answer",
    )
    grounding_note: str | None = Field(
        None,
        description="Honest note when context is thin, ambiguous, or retrieval failed",
    )
    sources: list[SourceCitation] = Field(
        default_factory=list,
        description="Citations tied to retrieved passages used in the answer",
    )
    session_id: str | None = Field(
        default=None,
        description="Use this on the next request to continue the same bounded conversation.",
    )
    audio: AudioMetadata | None = Field(
        None,
        description="Optional audio synthesis metadata (when include_tts=True and synthesis succeeded)",
    )
    tts_error: str | None = Field(
        None,
        description="When include_tts was True but synthesis failed, a short reason (e.g. clean-tts not running)",
    )
    retrieval: list[RetrievalHitSchema] = Field(
        default_factory=list,
        description="Top retrieval hits for debugging / transparency",
    )
    retrieval_error: str | None = Field(
        None,
        description="Set when the retrieval index could not be queried",
    )
