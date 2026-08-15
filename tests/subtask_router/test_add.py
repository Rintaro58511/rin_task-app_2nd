from unittest.mock import AsyncMock, MagicMock
import pytest
import uuid
from datetime import datetime, date
from fastapi import HTTPException

from models.tasks import Task
from enums import TaskStatus

from schemas.subtasks import UpdateAndCreateSubTaskSchema

from routers import subtasks
from routers.subtasks import create_subtask

@pytest.fixture
def subtask_schema():
    expeted_subtask_schema = UpdateAndCreateSubTaskSchema(
        subtask_name = "test_subtask",
        is_complete = True,
    )
    return expeted_subtask_schema

@pytest.fixture
def task():
    expeted_task = Task(
        task_id = uuid.uuid4(),
        user_id = uuid.uuid4(),
        task_name = "test_task",
        task_deadline = date(2026, 9, 20),
        task_detail = None,
        changed_time = datetime(2026, 8, 16),
        task_progress = TaskStatus.TODO,
        progress_ratio = 10,
        progress_comment = "少し進んだ"
    )
    return expeted_task

@pytest.mark.anyio
async def test_create_subtask(subtask_schema, task, monkeypatch):
    mock_db = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    task_id = uuid.uuid4()

    async def mock_fetch_task(task_id, mock_db):
        return task
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)
    async def mock_add_subtask(subtask_schema, task_id, mock_db):
        return None
    monkeypatch.setattr(subtasks, "add_subtask", mock_add_subtask)
    async def mock_calculate_ratio(task_id, db_session):
        return 50
    monkeypatch.setattr(subtasks, "calculate_ratio", mock_calculate_ratio)

    response = await create_subtask(subtask_schema, task_id, mock_db)

    assert response.message == "サブタスクを登録しました"
    assert task.progress_ratio == 50
    mock_db.flush.assert_awaited_once()
    mock_db.commit.assert_awaited_once()

@pytest.mark.anyio
async def test_create_none_subtask(subtask_schema, task, monkeypatch):
    mock_db = AsyncMock()
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    task_id = uuid.uuid4()

    async def mock_fetch_none_task(task_id, mock_db):
        return None
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_none_task)

    with pytest.raises(HTTPException) as exc_info:
        await create_subtask(subtask_schema, task_id, mock_db)

    assert exc_info.value.detail == "タスクが存在しません"
    assert exc_info.value.status_code == 404
    assert task.progress_ratio == 10
    mock_db.flush.assert_not_awaited()
    mock_db.commit.assert_not_awaited()