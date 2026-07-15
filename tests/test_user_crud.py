from unittest.mock import AsyncMock, MagicMock

import uuid

import pytest

from cruds import user
from cruds.user import fetch_user_by_email, add_user, authenticate_user
from models.user import User
from schemas.user import UserInDB


@pytest.mark.anyio
async def test_fetch_user_by_email():
    mock_db = AsyncMock()
    expected_user = User(
        user_id=uuid.uuid4(), user_name="rintaro", email="test@test.com"
    )

    mock_result = MagicMock()
    mock_db.execute.return_value = mock_result

    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.first.return_value = expected_user

    retrieved_user = await fetch_user_by_email("test@test.com", mock_db)

    assert retrieved_user.user_name == "rintaro"
    assert retrieved_user.email == "test@test.com"

    mock_db.execute.assert_called_once()


@pytest.mark.anyio
async def test_add_user():
    mock_db = AsyncMock()
    user_id = uuid.uuid4()
    expected_user = UserInDB(
        user_id=user_id,
        user_name="rintaro",
        email="test@test.com",
        hashed_password="hashed_test_pass",
    )

    returned_user = await add_user(expected_user, mock_db)

    assert returned_user.user_name == "rintaro"
    assert returned_user.email == "test@test.com"

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.anyio
async def test_authenticate_user(monkeypatch):
    mock_db = AsyncMock()

    mock_user = User(
        user_id=uuid.uuid4(),
        user_name="rintaro",
        email="test@test.com",
        hashed_password="hashed_test_password",  # 必要に応じて追加
    )

    async def mock_fetch_user_by_email(email, mock_db):
        return mock_user

    monkeypatch.setattr(user, "fetch_user_by_email", mock_fetch_user_by_email)
    monkeypatch.setattr("cruds.user.password_hash.verify", lambda p, h: True)

    returned_user = await authenticate_user("test@test.com", "test_password", mock_db)

    assert returned_user is not None
    assert returned_user.user_name == "rintaro"
    assert returned_user.email == "test@test.com"
