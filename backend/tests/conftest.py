import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rag.retrieve import reset_retrieval_index
from app.services.session_store import reset_session_store_for_tests


@pytest.fixture(autouse=True)
def _reset_backend_singletons() -> None:
    reset_retrieval_index()
    reset_session_store_for_tests()
    yield


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
