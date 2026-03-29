from __future__ import annotations

import re


_HEADING = re.compile(r"^#{1,3}\s+\S")


def split_markdown_sections(text: str) -> list[tuple[int, str, str]]:
    """
    Split markdown into (heading_level, section_title, body).
    Level 0 means a preamble before the first heading.
    """
    lines = text.splitlines()
    sections: list[tuple[int, str, str]] = []
    i = 0

    preamble_lines: list[str] = []
    while i < len(lines) and not _is_heading_line(lines[i]):
        preamble_lines.append(lines[i])
        i += 1
    preamble = "\n".join(preamble_lines).strip()
    if preamble:
        sections.append((0, "Preamble", preamble))

    while i < len(lines):
        line = lines[i]
        hm = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if not hm:
            i += 1
            continue
        level = len(hm.group(1))
        title = hm.group(2).strip()
        i += 1
        body_lines: list[str] = []
        while i < len(lines) and not _is_heading_line(lines[i]):
            body_lines.append(lines[i])
            i += 1
        body = "\n".join(body_lines).strip()
        sections.append((level, title, body))

    return sections


def _is_heading_line(line: str) -> bool:
    return bool(_HEADING.match(line.strip()))


def chunk_text_by_paragraphs(
    text: str,
    *,
    max_chars: int = 1200,
    overlap: int = 120,
) -> list[str]:
    """
    Split long text into chunks of roughly max_chars, preferring paragraph boundaries.
    Oversized paragraphs are split by sentences, then by fixed windows with overlap.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    if not paragraphs:
        return _hard_split(text, max_chars, overlap)

    chunks: list[str] = []
    current: list[str] = []
    cur_len = 0

    for para in paragraphs:
        if len(para) > max_chars:
            if current:
                chunks.append("\n\n".join(current).strip())
                current = []
                cur_len = 0
            chunks.extend(_split_long_block(para, max_chars, overlap))
            continue

        add = len(para) + (2 if current else 0)
        if cur_len + add <= max_chars:
            current.append(para)
            cur_len += add
        else:
            if current:
                chunks.append("\n\n".join(current).strip())
            current = [para]
            cur_len = len(para)

    if current:
        chunks.append("\n\n".join(current).strip())

    return chunks if chunks else _hard_split(text, max_chars, overlap)


def _split_long_block(text: str, max_chars: int, overlap: int) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) <= 1:
        return _hard_split(text, max_chars, overlap)

    out: list[str] = []
    buf: list[str] = []
    length = 0
    for s in sentences:
        add = len(s) + (1 if buf else 0)
        if length + add <= max_chars:
            buf.append(s)
            length += add
            continue
        if buf:
            out.append(" ".join(buf))
        if len(s) <= max_chars:
            buf = [s]
            length = len(s)
        else:
            out.extend(_hard_split(s, max_chars, overlap))
            buf = []
            length = 0
    if buf:
        out.append(" ".join(buf))
    return out if out else _hard_split(text, max_chars, overlap)


def _hard_split(text: str, max_chars: int, overlap: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    out: list[str] = []
    start = 0
    step = max(1, max_chars - overlap)
    while start < len(text):
        out.append(text[start : start + max_chars])
        start += step
    return out
