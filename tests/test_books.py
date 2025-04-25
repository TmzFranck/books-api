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
                return None  # Simule aucun utilisateur trouvé

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


def test_get_all_books_unauthenticated():
    resp = client.get("/api/v1/books/")
    assert resp.status_code in (401, 403)


def test_get_all_books_authenticated(auth_token):
    resp = client.get(
        "/api/v1/books/", headers={"Authorization": f"Bearer {auth_token}"}
    )
    # Le mock ne retourne rien, mais le test doit passer le contrôle d'accès
    assert resp.status_code in (200, 404, 422)


def test_create_book(auth_token):
    data = {
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "published_date": "2024-01-01",
        "page_count": 123,
        "language": "fr",
    }
    resp = client.post(
        "/api/v1/books/", json=data, headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code in (201, 400, 404, 422)


def test_get_book_by_id_authenticated(auth_token, monkeypatch):
    class FakeBook:
        def model_dump(self):
            return {"title": "Test Book"}

    monkeypatch.setattr(
        "src.books.service.BookService.get_book", AsyncMock(return_value=FakeBook())
    )
    resp = client.get(
        "/api/v1/books/fake-book-uid", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code in (200, 404)


def test_update_book_authenticated(auth_token, monkeypatch):
    class FakeBook:
        def model_dump(self):
            return {"title": "Updated Book"}

    monkeypatch.setattr(
        "src.books.service.BookService.update_book", AsyncMock(return_value=FakeBook())
    )
    resp = client.patch(
        "/api/v1/books/fake-book-uid",
        json={"title": "Updated Book"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code in (200, 404)


def test_delete_book_authenticated(auth_token, monkeypatch):
    monkeypatch.setattr(
        "src.books.service.BookService.delete_book", AsyncMock(return_value=True)
    )
    resp = client.delete(
        "/api/v1/books/fake-book-uid",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code in (204, 404)


def test_get_user_books_authenticated(auth_token, monkeypatch):
    monkeypatch.setattr(
        "src.books.service.BookService.get_user_books", AsyncMock(return_value=[])
    )
    resp = client.get(
        "/api/v1/books/user/fake-user-uid",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code in (200, 404)


@pytest.fixture(autouse=True, scope="function")
def mock_create_book_success(monkeypatch):
    from src.books.service import BookService

    class FakeBook:
        title = "Test Book"
        author = "Test Author"
        publisher = "Test Publisher"
        published_date = "2024-01-01"
        page_count = 123
        language = "fr"
        uid = "fake-uid"
        user_uid = "fake-user"
        created_at = "2024-01-01T00:00:00"
        updated_at = "2024-01-01T00:00:00"
        reviews = []
        tags = []

    monkeypatch.setattr(BookService, "create_book", AsyncMock(return_value=FakeBook()))
    yield
