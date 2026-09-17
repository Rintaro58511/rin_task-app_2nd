from datetime import date
import smtplib
from unittest.mock import MagicMock, AsyncMock

import service.emails
from service.emails import create_email, send_email, group_tasks_by_user


def test_create_email(test_user, task_list):

    test_msg = create_email(test_user.user_name, test_user.email, task_list)

    body = test_msg.get_content()

    assert task_list[0].task_name in body
    assert task_list[1].task_name in body
    assert task_list[0].task_detail in body
    assert task_list[1].task_detail in body
    assert test_msg["Subject"] == "test_user_aさん締め切りが近いまたは過ぎているタスクがあります。"
    assert test_msg["To"] == "test@user_a"


def test_send_email(monkeypatch):
    mock_smtp_class = MagicMock()
    mock_smtp_instance = MagicMock()
    mock_msg = MagicMock()

    mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance

    monkeypatch.setattr(smtplib, "SMTP", mock_smtp_class)

    monkeypatch.setattr(service.emails, "SMTP_USER", "test_user")
    monkeypatch.setattr(service.emails, "SMTP_PASSWORD", "test_password")

    send_email(mock_msg)

    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("test_user", "test_password")
    mock_smtp_instance.send_message.assert_called_once_with(mock_msg)

def test_group_tasks_by_user(test_user, test_other_user, task_list, task_list2):

    result = group_tasks_by_user([
        (task_list[0], test_user),
        (task_list[1], test_user),
        (task_list2[0], test_other_user),
        (task_list2[1], test_other_user),
    ])

    assert result[test_user.user_id]["tasks"] == task_list
    assert result[test_other_user.user_id]["tasks"] == task_list2
