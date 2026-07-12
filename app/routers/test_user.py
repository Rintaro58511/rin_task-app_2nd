import routers.user as user
from fastapi.testclient import TestClient
from main import app
from models.user import User
from unittest.mock import AsyncMock
import db
import pytest
import uuid

client = TestClient(app)


@pytest.fixture
def override_get_db():

    async def override_db():
        yield AsyncMock()

    app.dependency_overrides[db.get_db_session] = override_db

    yield

    app.dependency_overrides.clear()


def test_signup_user(monkeypatch, override_get_db):
    async def mock_add_user(user, db):
        return User(user_id=uuid.uuid4(), user_name="rintaro", email="test@test.com")

    monkeypatch.setattr(user, "add_user", mock_add_user)

    response = client.post(
        "/user/signup",
        json={
            "user_name": "rintaro",
            "email": "test@test.com",
            "hashed_password": "dummy_hash",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "ユーザーの登録ができました。"

    assert body["user"]["user_name"] == "rintaro"

    assert body["user"]["email"] == "test@test.com"
