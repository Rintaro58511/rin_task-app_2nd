import pytest
from unittest.mock import AsyncMock

from fastapi import HTTPException

from routers.subtasks import update_subtask
from routers import subtasks

@pytest.mark.anyio
async def test_update_subtask(subtask_schema, subtask, task, monkeypatch):
    mock_db = AsyncMock()

    async def mock_fetch_task(task_id, db_session):
        return task
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)

    async def mock_fetch_subtask(subtask_id, db_session):
        return subtask
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)

    async def mock_modify_subtask(subtask_schema, target_subtask):
        return None
    monkeypatch.setattr(subtasks, "modify_subtask", mock_modify_subtask)

    async def mock_calculate_ratio(task_id, db_session):
        return 50
    monkeypatch.setattr(subtasks, "calculate_ratio", mock_calculate_ratio)

    response = await update_subtask(subtask_schema, subtask.subtask_id, subtask.task_id, mock_db)

    assert response.message == "サブタスクを更新しました"
    assert task.progress_ratio == 50
    mock_db.flush.assert_awaited_once()
    mock_db.commit.assert_awaited_once()

@pytest.mark.anyio
async def test_update_none_task(subtask_schema, subtask, monkeypatch):
    mock_db = AsyncMock()

    async def mock_fetch_none_task(task_id, db_session):
        return None
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_none_task)

    with pytest.raises(HTTPException) as exc_info:
        await update_subtask(subtask_schema, subtask.subtask_id, subtask.task_id, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "指定されたタスクが存在しません"

@pytest.mark.anyio
async def test_update_none_subtask(subtask_schema, task, subtask, monkeypatch):
    mock_db = AsyncMock()

    async def mock_fetch_task(task_id, db_session):
        return task
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)

    async def mock_fetch_none_subtask(subtask_id, db_session):
        return None
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_none_subtask)

    with pytest.raises(HTTPException) as exc_info:
        await update_subtask(subtask_schema, subtask.subtask_id, subtask.task_id, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "指定されたサブタスクが存在しません"

@pytest.mark.anyio
async def test_update_other_task(subtask_schema, task, subtask, other_task, monkeypatch):
    mock_db = AsyncMock()

    async def mock_fetch_task(task_id, db_session):
        return task
    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)

    async def mock_fetch_none_subtask(subtask_id, db_session):
        return subtask
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_none_subtask)

    with pytest.raises(HTTPException) as exc_info:
        await update_subtask(subtask_schema, subtask.subtask_id, other_task.task_id, mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "親タスクが異なります"
