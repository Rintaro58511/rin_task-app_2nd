import os

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app
from routers import user


@pytest.fixture
def override_get_test_current_user(test_user):
    """E2Eテスト用のユーザー情報"""

    async def override_test_user():
        smtp_user = os.getenv("SMTP_USER")
        test_user.email = smtp_user
        yield test_user

    app.dependency_overrides[user.get_current_user] = override_test_user

    yield

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_alert_deadline_sends_real_email(
    integration_test,
    override_get_test_db,
    override_get_test_current_user,
):

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/emails/alert_deadline")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "メールを送信しました"
