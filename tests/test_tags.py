import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from src.__init__ import app
from src.auth.utils import create_access_token

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def override_dependencies():
    async def fake_exec(statement):
        class FakeResult:
            def first(self):
                return None

        return FakeResult()

    fake_session = MagicMock()
    fake_session.exec = AsyncMock(side_effect=fake_exec)

    async def fake_get_session():
        yield fake_session

    app.dependency_overrides = {}
    from src.database.main import get_session

    app.dependency_overrides[get_session] = fake_get_session
    with patch(
        "src.database.redis.token_block_list",
        new=MagicMock(get=AsyncMock(return_value=None)),
    ), patch("src.database.redis.add_jti_to_block_list", new=AsyncMock()), patch(
        "src.database.redis.token_in_blocklist", new=AsyncMock(return_value=False)
    ), patch(
        "src.celery_tasks.send_email", new=AsyncMock()
    ):
        yield
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def auth_token():
    user_data = {"email": "test@example.com", "user_uid": "fake-uid"}
    return create_access_token(user_data=user_data)


def test_get_all_tags_unauthenticated():
    resp = client.get("/api/v1/tags/")
    assert resp.status_code in (401, 403)


def test_get_all_tags_authenticated(auth_token):
    resp = client.get(
        "/api/v1/tags/", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code in (200, 404)


@pytest.fixture(autouse=True, scope="function")
def mock_get_tags_success(monkeypatch):
    from src.tags.service import TagService

    class FakeTag:
        pass

    monkeypatch.setattr(TagService, "get_tags", AsyncMock(return_value=[FakeTag()]))
    yield


# Ajoute d'autres tests pour POST, PUT, DELETE, erreurs, etc.
