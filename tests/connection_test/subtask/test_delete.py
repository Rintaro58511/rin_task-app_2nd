import uuid

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from main import app
from models.subtasks import SubTask
from sqlalchemy import select


@pytest.mark.asyncio
async def test_delete_subtask(
    connection_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(f"/tasks/{test_task.task_id}/subtasks/{test_subtask.subtask_id}")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json()["message"] == "サブタスクを削除しました"
    result = await db_session.execute(select(SubTask).where(SubTask.subtask_name == "test_subtask"))
    deleted_subtask = result.scalar_one_or_none()

    assert deleted_subtask is None


@pytest.mark.asyncio
async def test_fail_find_task(
    connection_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    none_task_id = uuid.uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(f"/tasks/{none_task_id}/subtasks/{test_subtask.subtask_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["detail"] == "指定されたタスクが存在しません"
    result = await db_session.execute(select(SubTask).where(SubTask.subtask_name == "test_subtask"))
    deleted_subtask = result.scalar_one_or_none()

    assert deleted_subtask is not None


@pytest.mark.asyncio
async def test_fail_find_subtask(
    connection_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    none_subtask_id = uuid.uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(f"/tasks/{test_task.task_id}/subtasks/{none_subtask_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json()["detail"] == "指定されたサブタスクが存在しません"
    result = await db_session.execute(select(SubTask).where(SubTask.subtask_name == "test_subtask"))
    deleted_subtask = result.scalar_one_or_none()

    assert deleted_subtask is not None


@pytest.mark.asyncio
async def test_find_other_task(
    connection_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(
            f"/tasks/{other_task.task_id}/subtasks/{test_subtask.subtask_id}"
        )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
    assert response.json()["detail"] == "親タスクが異なります"
    result = await db_session.execute(select(SubTask).where(SubTask.subtask_name == "test_subtask"))
    deleted_subtask = result.scalar_one_or_none()

    assert deleted_subtask is not None
