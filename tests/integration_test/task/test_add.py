from datetime import date

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from enums import TaskStatus
from main import app
from models.tasks import Task


@pytest.mark.asyncio
async def test_add_task(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    payload = {
        "task_name": "integration_test_task",
        "task_deadline": "2026-10-10",
        "task_detail": "test_task",
        "task_status": {
            "task_progress": TaskStatus.TODO,
            "progress_ratio": 0,
            "progress_comment": None,
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tasks", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "タスクを登録しました"
    result = await db_session.execute(
        select(Task).where(
            Task.task_name == "integration_test_task",
            Task.task_deadline == date(2026, 10, 10),
            Task.task_detail == "test_task",
            Task.task_progress == TaskStatus.TODO,
            Task.user_id == test_user.user_id,
        )
    )
    created_task = result.scalar_one_or_none()

    assert created_task is not None


@pytest.mark.asyncio
async def test_add_expired_task(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    payload = {
        "task_name": "integration_test_task",
        "task_deadline": "2026-08-10",
        "task_detail": "test_task",
        "task_status": {
            "task_progress": TaskStatus.TODO,
            "progress_ratio": 0,
            "progress_comment": None,
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/tasks", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "期限が過去の日付になっています"
    result = await db_session.execute(
        select(Task).where(
            Task.task_name == "integration_test_task",
            Task.task_deadline == date(2026, 8, 10),
            Task.task_detail == "test_task",
            Task.task_progress == TaskStatus.TODO,
            Task.user_id == test_user.user_id,
        )
    )
    created_task = result.scalar_one_or_none()

    assert created_task is None
