import pytest
from fastapi import HTTPException
import jwt

from routers.user import get_current_user  # 実際のパスに合わせて修正
from routers.user import SECRET_KEY, ALGORITHM

@pytest.mark.anyio
async def test_get_current_user_success(monkeypatch, test_user, db_session):

    token = jwt.encode(
        {"sub": test_user.email},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    async def mock_fetch_user_by_email(email, db):
        return test_user

    monkeypatch.setattr(
        "routers.user.fetch_user_by_email",
        mock_fetch_user_by_email,
    )

    result = await get_current_user(
        token=token,
        db_session=db_session,
    )

    assert result == test_user

@pytest.mark.anyio
async def test_get_current_user_without_sub(db_session):

    token = jwt.encode(
        {"user_id": "123"},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            token=token,
            db_session=db_session,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "認証に失敗しました"

@pytest.mark.anyio
async def test_get_current_user_invalid_token(db_session):

    invalid_token = "invalid.token.value"

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            token=invalid_token,
            db_session=db_session,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "認証に失敗しました"

@pytest.mark.anyio
async def test_get_current_user_user_not_found(monkeypatch, db_session):

    token = jwt.encode(
        {"sub": "notfound@example.com"},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    async def mock_fetch_user_by_email(email, db):
        return None

    monkeypatch.setattr(
        "routers.user.fetch_user_by_email",
        mock_fetch_user_by_email,
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            token=token,
            db_session=db_session,
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "認証に失敗しました"