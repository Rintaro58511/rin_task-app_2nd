import routers.user as user
from httpx import ASGITransport, AsyncClient
from main import app
from models.user import User
from unittest.mock import AsyncMock
import db
import pytest
import uuid
from fastapi import HTTPException, status


@pytest.fixture
def override_get_db():

    async def override_db():
        yield AsyncMock()

    app.dependency_overrides[db.get_db_session] = override_db

    yield

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_signup_user(monkeypatch, override_get_db):
    async def mock_add_user(user, db):
        return User(user_id=uuid.uuid4(), user_name="rintaro", email="test@test.com")

    monkeypatch.setattr(user, "add_user", mock_add_user)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/user/signup",
            json={
                "user_name": "rintaro",
                "email": "test@test.com",
                "hashed_password": "dummy_password",
            },
        )
    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "ユーザーの登録ができました。"

    assert body["user"]["user_name"] == "rintaro"

    assert body["user"]["email"] == "test@test.com"


@pytest.mark.anyio
async def test_signup_user_db_error(monkeypatch, override_get_db):
    async def mock_add_user_fail(user, db):
        raise Exception("Database Connection Timeout")

    monkeypatch.setattr(user, "add_user", mock_add_user_fail)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/user/signup",
            json={
                "user_name": "rintaro",
                "email": "test@test.com",
                "hashed_password": "dummy_hash",
            },
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert body["detail"] == "ユーザーの登録に失敗しました。"


@pytest.mark.anyio
async def test_signup_user_already_exists(monkeypatch, override_get_db):
    async def mock_add_user_http_fail(user, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="このメールアドレスは既に登録されています。",
        )

    monkeypatch.setattr(user, "add_user", mock_add_user_http_fail)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/user/signup",
            json={
                "user_name": "rintaro",
                "email": "test@test.com",
                "hashed_password": "dummy_hash",
            },
        )

    assert response.status_code == status.HTTP_409_CONFLICT
    body = response.json()
    assert body["detail"] == "このメールアドレスは既に登録されています。"
