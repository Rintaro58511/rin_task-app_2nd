import smtplib
from unittest.mock import AsyncMock, MagicMock

import pytest

import service.emails
from service.emails import create_email, group_tasks_by_user, send_deadline_notifications, send_email


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

    result = group_tasks_by_user(
        [
            (task_list[0], test_user),
            (task_list[1], test_user),
            (task_list2[0], test_other_user),
            (task_list2[1], test_other_user),
        ]
    )

    assert result[test_user.user_id]["tasks"] == task_list
    assert result[test_other_user.user_id]["tasks"] == task_list2


@pytest.mark.asyncio
async def test_send_deadline_notifications(
    monkeypatch, test_user, test_other_user, task_list, task_list2
):
    mock_db = AsyncMock()

    fetch_mock = AsyncMock(
        return_value=[
            (task_list[0], test_user),
            (task_list[1], test_user),
            (task_list2[0], test_other_user),
            (task_list2[1], test_other_user),
        ]
    )

    group_mock = MagicMock(
        return_value={
            test_user.user_id: {
                "user": test_user,
                "tasks": task_list,
            },
            test_other_user.user_id: {
                "user": test_other_user,
                "tasks": task_list2,
            },
        }
    )

    send_mock = AsyncMock()

    monkeypatch.setattr(service.emails, "fetch_all_deadline_tasks", fetch_mock)

    monkeypatch.setattr(service.emails, "group_tasks_by_user", group_mock)

    monkeypatch.setattr(service.emails, "create_and_send_email", send_mock)

    await send_deadline_notifications(mock_db)

    fetch_mock.assert_awaited_once()
    group_mock.assert_called_once()
    assert send_mock.await_count == 2

    send_mock.assert_any_await(
        test_user.user_name,
        test_user.email,
        task_list,
    )

    send_mock.assert_any_await(
        test_other_user.user_name,
        test_other_user.email,
        task_list2,
    )
