import pytest
from httpx import ASGITransport, AsyncClient

from main import app

from schemas.subtasks import UpdateAndCreateSubTaskSchema

from routers import subtasks

from enums import TaskStatus


@pytest.mark.asyncio
async def test_create_subtask(monkeypatch, task, subtask_schema, override_get_db, override_get_current_user):

    async def mock_fetch_task(task_id, user_id, db):
        return task
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)
    
    async def mock_add_subtask(subtask, task_id, db):
        return UpdateAndCreateSubTaskSchema(
            subtask_name="test_subtask",
            is_complete=False,
        )
    monkeypatch.setattr(subtasks, "add_subtask", mock_add_subtask)

    async def mock_calculate_ratio(task_id, user_id, db):
        return 50
    monkeypatch.setattr(subtasks, "calculate_ratio", mock_calculate_ratio)

    async def mock_check_progress(progress_ratio, db_session):
        return TaskStatus.IN_PROGRESS
    monkeypatch.setattr(subtasks, "check_progress", mock_check_progress)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            f"/tasks/{task.task_id}/subtask",
            json = subtask_schema.model_dump()
        )
    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "サブタスクを登録しました"

@pytest.mark.asyncio
async def test_fail_create_subtask(monkeypatch, task, subtask_schema, override_get_db, override_get_current_user):

    async def mock_fetch_task(task_id, user_id, db):
        return None
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            f"/tasks/{task.task_id}/subtask",
            json = subtask_schema.model_dump()
        )
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "タスクが存在しません"
