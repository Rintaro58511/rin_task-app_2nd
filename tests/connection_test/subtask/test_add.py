import uuid

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from main import app
from models.subtasks import SubTask


@pytest.mark.asyncio
async def test_add_subtask(
    connection_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    payload = {
        "subtask_name": "integration_test_subtask",
        "is_complete": False,
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(f"/tasks/{test_task.task_id}/subtask", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "サブタスクを登録しました"
    result = await db_session.execute(
        select(SubTask).where(SubTask.subtask_name == "integration_test_subtask")
    )
    created_subtask = result.scalar_one_or_none()

    assert created_subtask is not None


@pytest.mark.asyncio
async def test_fail_add_subtask(
    connection_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    payload = {
        "subtask_name": "integration_test_subtask",
        "is_complete": False,
    }

    none_task_id = uuid.uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(f"/tasks/{none_task_id}/subtask", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "タスクが存在しません"
    result = await db_session.execute(
        select(SubTask).where(SubTask.subtask_name == "integration_test_subtask")
    )
    created_subtask = result.scalar_one_or_none()

    assert created_subtask is None
