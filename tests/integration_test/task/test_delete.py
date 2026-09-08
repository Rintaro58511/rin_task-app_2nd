import uuid

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from main import app
from models.tasks import Task


@pytest.mark.asyncio
async def test_delete_subtask(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(f"/tasks/{test_task.task_id}")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["message"] == "タスクを削除しました"
    result = await db_session.execute(select(Task).where(Task.task_id == test_task.task_id))
    deleted_task = result.scalar_one_or_none()

    assert deleted_task is None


@pytest.mark.asyncio
async def test_fail_find_task(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    none_task_id = uuid.uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(f"/tasks/{none_task_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["detail"] == "指定されたタスクが見つかりません"
    result = await db_session.execute(select(Task).where(Task.task_id == test_task.task_id))
    deleted_task = result.scalar_one_or_none()

    assert deleted_task is not None
