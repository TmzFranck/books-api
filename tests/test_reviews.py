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


def test_get_all_reviews_unauthenticated():
    resp = client.get("/api/v1/reviews/")
    assert resp.status_code in (401, 403)


def test_get_all_reviews_authenticated(auth_token):
    resp = client.get(
        "/api/v1/reviews/", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code in (200, 404)


@pytest.fixture(autouse=True, scope="function")
def mock_get_reviews_success(monkeypatch):
    from src.reviews.service import ReviewService

    class FakeReview:
        pass

    monkeypatch.setattr(
        ReviewService, "get_all_reviews", AsyncMock(return_value=[FakeReview()])
    )
    yield


def test_get_review_by_id_authenticated(auth_token, monkeypatch):
    class FakeReview:
        pass

    monkeypatch.setattr(
        "src.reviews.service.ReviewService.get_review",
        AsyncMock(return_value=FakeReview()),
    )
    resp = client.get(
        "/api/v1/reviews/fake-review-uid",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code in (200, 404)


def test_create_review_authenticated(auth_token, monkeypatch):
    class FakeReview:
        pass

    monkeypatch.setattr(
        "src.reviews.service.ReviewService.add_review_to_book",
        AsyncMock(return_value=FakeReview()),
    )
    resp = client.post(
        "/api/v1/reviews/book/fake-book-uid",
        json={"content": "Great!", "rating": 5},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code in (200, 201, 404)


def test_delete_review_authenticated(auth_token, monkeypatch):
    monkeypatch.setattr(
        "src.reviews.service.ReviewService.delete_review_to_form_book",
        AsyncMock(return_value=True),
    )
    resp = client.delete(
        "/api/v1/reviews/fake-review-uid",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code in (204, 404)
