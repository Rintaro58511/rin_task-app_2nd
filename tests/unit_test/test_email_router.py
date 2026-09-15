from unittest.mock import AsyncMock

import pytest

from routers import emails
from routers.emails import alert_deadline


@pytest.mark.anyio
async def test_alert_deadline(monkeypatch, test_user, task_list):
    mock_db = AsyncMock()

    async def mock_fetch_deadline_tasks(user_id, mock_db):
        return task_list

    monkeypatch.setattr(emails, "fetch_deadline_tasks", mock_fetch_deadline_tasks)

    async def mock_create_and_send_email(user_name, email, task_list):
        return None

    monkeypatch.setattr(emails, "create_and_send_email", mock_create_and_send_email)

    response = await alert_deadline(test_user, mock_db)

    assert response.message == "メールを送信しました"
