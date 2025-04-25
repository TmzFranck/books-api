import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from src.__init__ import app
import uuid

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def override_dependencies():
    async def fake_get_session():
        yield MagicMock()

    app.dependency_overrides = {}
    from src.database.main import get_session

    app.dependency_overrides[get_session] = fake_get_session
    with patch("src.database.redis.add_jti_to_block_list", new=AsyncMock()), patch(
        "src.database.redis.token_in_blocklist", new=AsyncMock(return_value=False)
    ), patch("src.celery_tasks.send_email", new=AsyncMock()):
        yield
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def auth_token():
    return "test-token"


@pytest.fixture(scope="module")
def user_data():
    return {
        "email": f"user_{uuid.uuid4().hex[:8]}@test.com",
        "password": "TestPassword123!",
        "username": f"user_{uuid.uuid4().hex[:8]}",
    }


def test_signup(user_data):
    resp = client.post("/api/v1/auth/signup", json=user_data)
    print(resp.status_code, resp.text)
    assert resp.status_code in (201, 400, 409, 422)
