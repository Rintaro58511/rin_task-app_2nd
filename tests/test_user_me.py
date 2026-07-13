import routers.user as user
from httpx import ASGITransport, AsyncClient
from main import app
from models.user import User
from unittest.mock import AsyncMock
import db
import pytest
import uuid
from fastapi import HTTPException, status
import jwt
from routers.user import SECRET_KEY, ALGORITHM, create_access_token


@pytest.fixture
def override_get_db():

    async def override_db():
        yield AsyncMock()

    app.dependency_overrides[db.get_db_session] = override_db

    yield

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_my_info_success(monkeypatch, override_get_db):

    async def mock_fetch_user_by_email(email, db_session):
        return User(user_id=uuid.uuid4(), user_name="rintaro", email="test@test.com")

    monkeypatch.setattr(user, "fetch_user_by_email", mock_fetch_user_by_email)

    token = create_access_token(data={"sub": "test@test.com"})

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/user/me", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "ユーザ情報を取得しました。"
    assert body["user"]["user_name"] == "rintaro"
    assert body["user"]["email"] == "test@test.com"
