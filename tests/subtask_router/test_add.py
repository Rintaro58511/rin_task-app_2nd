from unittest.mock import AsyncMock
import pytest
import uuid
from fastapi import HTTPException

from routers import subtasks
from routers.subtasks import create_subtask

from enums import TaskStatus

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

    async def mock_check_progress(progress_ratio, db_session):
        return TaskStatus.IN_PROGRESS
    monkeypatch.setattr(subtasks, "check_progress", mock_check_progress)

    response = await create_subtask(subtask_schema, task_id, mock_db)

    assert response.message == "サブタスクを登録しました"
    assert task.progress_ratio == 50
    assert task.task_progress == TaskStatus.IN_PROGRESS
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
    assert task.progress_ratio == 80
    mock_db.flush.assert_not_awaited()
    mock_db.commit.assert_not_awaited()