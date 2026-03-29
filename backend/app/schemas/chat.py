from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: str | None = Field(
        default=None,
        description="Optional id to continue a short multi-turn chat; omit to start a new session.",
    )


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
    """Structured citation for passages the answer relied on."""

    chunk_id: str
    source_file: str
    section_title: str
    content_type: str
    score: float = Field(..., description="Retrieval relevance score for this chunk")
    excerpt: str = Field(..., description="Short excerpt from the chunk text")


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
    retrieval: list[RetrievalHitSchema] = Field(
        default_factory=list,
        description="Top-k retrieved chunks (for inspection / debugging)",
    )
    retrieval_error: str | None = Field(
        None,
        description="Set when the chunk index could not be loaded",
    )
