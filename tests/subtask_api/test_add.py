import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock

from main import app

from schemas.subtasks import UpdateAndCreateSubTaskSchema

from routers import subtasks

from enums import TaskStatus

import db

@pytest.fixture
def override_get_db():

    async def override_db():
        yield AsyncMock()

    app.dependency_overrides[db.get_db_session] = override_db

    yield

    app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_create_subtask(monkeypatch, task, subtask_schema, override_get_db):

    async def mock_fetch_task(task_id, db):
        return task
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)
    
    async def mock_add_subtask(subtask, task_id, db):
        return UpdateAndCreateSubTaskSchema(
            subtask_name="test_subtask",
            is_complete=False,
        )
    monkeypatch.setattr(subtasks, "add_subtask", mock_add_subtask)

    async def mock_calculate_ratio(task_id, db):
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

@pytest.mark.anyio
async def test_fail_create_subtask(monkeypatch, task, subtask_schema, override_get_db):

    async def mock_fetch_task(task_id, db):
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
