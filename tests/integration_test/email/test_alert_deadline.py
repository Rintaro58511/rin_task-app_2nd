import smtplib
from unittest.mock import MagicMock

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

import service.emails
from main import app


@pytest.mark.asyncio
async def test_alert_deadline(
    integration_test, override_get_test_db, override_get_test_current_user, monkeypatch
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    mock_smtp_class = MagicMock()
    mock_smtp_instance = MagicMock()

    mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance

    monkeypatch.setattr(smtplib, "SMTP", mock_smtp_class)

    monkeypatch.setattr(service.emails, "SMTP_USER", "test_user")
    monkeypatch.setattr(service.emails, "SMTP_PASSWORD", "test_password")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/emails/alert_deadline")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "メールを送信しました"

    args, _ = mock_smtp_instance.send_message.call_args
    test_msg = args[0]
    body = test_msg.get_content()
    mock_smtp_instance.send_message.assert_called_once()

    assert test_task.task_name not in body
    assert other_task.task_name in body
    assert str(test_task.progress_ratio) not in body
    assert str(other_task.progress_ratio) in body
    assert (
        test_msg["Subject"]
        == f"{test_user.user_name}さん締め切りが近いまたは過ぎているタスクがあります。"
    )
    assert test_msg["To"] == test_user.email
