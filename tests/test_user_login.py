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
async def test_login_for_access_token(monkeypatch, override_get_db):

    async def mock_authenticate_user(username, password, db):
        return User(user_id=uuid.uuid4(), user_name="rintaro", email="test@test.com")

    monkeypatch.setattr(user, "authenticate_user", mock_authenticate_user)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/user/token",
            data={
                "username": "test@test.com",
                "password": "dummy_password",
            },
        )
    assert response.status_code == 200
    body = response.json()

    assert "access_token" in body

    assert body["token_type"] == "bearer"
