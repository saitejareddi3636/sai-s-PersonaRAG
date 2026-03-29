from __future__ import annotations

from typing import Any, TypedDict


class ChunkRecord(TypedDict, total=False):
    id: str
    content_type: str
    source_file: str
    section_title: str
    section_level: int
    text: str
    metadata: dict[str, Any]


class RetrievalHit:
    __slots__ = (
        "id",
        "score",
        "content_type",
        "source_file",
        "section_title",
        "section_level",
        "text",
        "metadata",
    )

    def __init__(
        self,
        *,
        id: str,
        score: float,
        content_type: str,
        source_file: str,
        section_title: str,
        section_level: int,
        text: str,
        metadata: dict[str, Any],
    ) -> None:
        self.id = id
        self.score = score
        self.content_type = content_type
        self.source_file = source_file
        self.section_title = section_title
        self.section_level = section_level
        self.text = text
        self.metadata = metadata

    def to_api_dict(self, *, text_preview_chars: int = 240) -> dict[str, Any]:
        preview = self.text.strip().replace("\n", " ")
        if len(preview) > text_preview_chars:
            preview = preview[:text_preview_chars] + "…"
        return {
            "id": self.id,
            "score": round(self.score, 6),
            "content_type": self.content_type,
            "source_file": self.source_file,
            "section_title": self.section_title,
            "section_level": self.section_level,
            "text_preview": preview,
            "metadata": self.metadata,
        }
