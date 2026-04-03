"""Tests for curated interview fast path."""

from app.services import prepared_interview as pi


def setup_function() -> None:
    pi.reload_prepared_interview_cache()


def test_match_exact_prompt() -> None:
    assert pi.match_prepared_answer("Tell me about yourself") is not None


def test_match_paraphrase_avtar() -> None:
    out = pi.match_prepared_answer("What did you do at Avtar?")
    assert out is not None
    assert "Avtar" in out


def test_match_when_start() -> None:
    out = pi.match_prepared_answer("When can you start?")
    assert out is not None
    assert "May 2026" in out


def test_no_match_gibberish() -> None:
    assert pi.match_prepared_answer("xyzabc nonsense query 12345") is None
