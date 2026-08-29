import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from enums import TaskStatus
from main import app
from routers import subtasks


@pytest.mark.anyio
async def test_delete_subtask(
    monkeypatch,
    task,
    subtask,
    override_get_db,
    override_get_current_user
    ):

    async def mock_fetch_task(task_id, user_id, db):
        return task
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)

    async def mock_fetch_subtask(task_id, user_id, db):
        return subtask
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)
    
    async def mock_remove_subtask(target_subtask, db):
        return None
    monkeypatch.setattr(subtasks, "remove_subtask", mock_remove_subtask)

    async def mock_calculate_ratio(task_id, user_id, db):
        return 50
    monkeypatch.setattr(subtasks, "calculate_ratio", mock_calculate_ratio)

    async def mock_check_progress(progress_ratio, db_session):
        return TaskStatus.IN_PROGRESS
    monkeypatch.setattr(subtasks, "check_progress", mock_check_progress)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.delete(
            f"/tasks/{task.task_id}/subtasks/{subtask.subtask_id}"
        )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["message"] == "サブタスクを削除しました"

@pytest.mark.anyio
async def test_delete_none_task(
    monkeypatch,
    subtask,
    task,
    override_get_db,
    override_get_current_user
    ):

    async def mock_fetch_none_task(task_id, user_id, db):
        return None
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_none_task)
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.delete(
            f"/tasks/{task.task_id}/subtasks/{subtask.subtask_id}"
        )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body["detail"] == "指定されたタスクが存在しません"

@pytest.mark.anyio
async def test_delete_none_subtask(
    monkeypatch,
    subtask,
    task,
    override_get_db,
    override_get_current_user
    ):

    async def mock_fetch_task(task_id, user_id, db):
        return task
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)

    async def mock_fetch_none_subtask(subtask_id, user_id, db):
        return None
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_none_subtask)
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.delete(
            f"/tasks/{task.task_id}/subtasks/{subtask.subtask_id}"
        )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body["detail"] == "指定されたサブタスクが存在しません"

@pytest.mark.anyio
async def test_delete_other_task(
    monkeypatch,
    subtask,
    task,
    other_task,
    override_get_db,
    override_get_current_user):

    async def mock_fetch_task(task_id, user_id, db):
        return task
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)

    async def mock_fetch_subtask(subtask_id, user_id, db):
        return subtask
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.delete(
            f"/tasks/{other_task.task_id}/subtasks/{subtask.subtask_id}"
        )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert body["detail"] == "親タスクが異なります"
