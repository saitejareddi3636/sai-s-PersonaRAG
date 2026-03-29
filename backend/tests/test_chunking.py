from app.rag.chunking import chunk_text_by_paragraphs, split_markdown_sections


def test_split_markdown_sections_basic() -> None:
    text = "# Title\n\nIntro body.\n\n## Sub\n\nMore here."
    sections = split_markdown_sections(text)
    assert len(sections) == 2
    assert sections[0] == (1, "Title", "Intro body.")
    assert sections[1] == (2, "Sub", "More here.")


def test_split_markdown_preamble() -> None:
    text = "Preamble only.\n\n# First\n\nBody."
    sections = split_markdown_sections(text)
    assert sections[0][0] == 0
    assert sections[0][1] == "Preamble"
    assert sections[1] == (1, "First", "Body.")


def test_chunk_text_respects_small_paragraphs() -> None:
    t = "a\n\nb\n\nc"
    out = chunk_text_by_paragraphs(t, max_chars=100, overlap=10)
    assert len(out) == 1
    assert "a" in out[0]
