import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rag.retrieve import reset_retrieval_index
from app.services.session_store import reset_session_store_for_tests


def pytest_report_header(config):
    return [
        "PersonaRAG: default tests are in-process (TestClient).",
        "  LLM (/api/chat): needs Ollama at OLLAMA_BASE_URL with OLLAMA_CHAT_MODEL pulled.",
        "  Real STT+TTS: RUN_VOICE_SMOKE=1 pytest tests/test_voice_stack_smoke.py -s",
        "  Live HTTP (docker/VM API): LIVE_API_BASE=http://127.0.0.1:8000 pytest tests/test_api_stack_live_http.py -s",
        "  Script (same as live): python scripts/check_stack.py",
    ]


def pytest_sessionfinish(session, exitstatus):
    try:
        reporter = session.config.pluginmanager.get_plugin("terminalreporter")
        if reporter is None:
            return
        reporter.write_sep("=", "PersonaRAG — if STT/TTS/LLM were not exercised")
        reporter.write_line(
            "  • Most pytest tests do not call Faster-Whisper or Piper unless RUN_VOICE_SMOKE=1."
        )
        reporter.write_line(
            "  • Voice route tests often mock STT; they validate wiring, not model quality."
        )
        reporter.write_line(
            "  • In-process LLM/STT/TTS smoke: pytest tests/test_stack_output_report.py -v"
        )
        reporter.write_line(
            "  • Live HTTP: start API, then python scripts/check_stack.py "
            "or LIVE_API_BASE=... pytest tests/test_api_stack_live_http.py -s"
        )
    except Exception:
        return


@pytest.fixture(autouse=True)
def _reset_backend_singletons() -> None:
    reset_retrieval_index()
    reset_session_store_for_tests()
    yield


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
