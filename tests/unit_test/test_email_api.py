import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app
from routers import emails


@pytest.mark.asyncio
async def test_email_post(monkeypatch, override_get_mock_db, override_get_current_user, task_list):

    async def mock_fetch_deadline_tasks(user_id, mock_db):
        return task_list

    monkeypatch.setattr(emails, "fetch_deadline_tasks", mock_fetch_deadline_tasks)

    async def mock_create_and_send_email(user_name, email, task_list):
        return None

    monkeypatch.setattr(emails, "create_and_send_email", mock_create_and_send_email)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/emails/alert_deadline")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "メールを送信しました"
