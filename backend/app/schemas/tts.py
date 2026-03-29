from typing import Literal

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    """Request to synthesize text into audio."""

    text: str = Field(..., min_length=1, description="Text to synthesize into speech")
    voice_profile_id: str | None = Field(
        default=None,
        description="Optional voice profile ID; if omitted, uses default voice",
    )


class TTSResponse(BaseModel):
    """Response containing synthesized audio metadata and reference."""

    success: bool = Field(
        ..., description="Whether synthesis succeeded or failed"
    )
    audio_url: str | None = Field(
        None,
        description="URL to access the synthesized audio (when success=true)",
    )
    audio_path: str | None = Field(
        None,
        description="Local file path to audio (internal reference when success=true)",
    )
    duration_ms: int | None = Field(
        None, description="Duration of synthesized audio in milliseconds"
    )
    provider: str = Field(
        default="f5-tts", description="TTS provider that synthesized this audio"
    )
    message: str | None = Field(
        None, description="Status message or error details"
    )
