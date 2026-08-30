import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status

from enums import TaskStatus
from routers import subtasks
from routers.subtasks import update_subtask


@pytest.mark.anyio
async def test_update_subtask(subtask_schema, subtask, task, monkeypatch):
    mock_db = AsyncMock()
    current_user = MagicMock()
    current_user.user_id = uuid.uuid4()

    async def mock_fetch_task(task_id, user_id, db_session):
        return task

    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)

    async def mock_fetch_subtask(subtask_id, user_id, db_session):
        return subtask

    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)

    async def mock_modify_subtask(subtask_schema, target_subtask):
        return None

    monkeypatch.setattr(subtasks, "modify_subtask", mock_modify_subtask)

    async def mock_calculate_ratio(task_id, user_id, db_session):
        return 50

    monkeypatch.setattr(subtasks, "calculate_ratio", mock_calculate_ratio)

    async def mock_check_progress(progress_ratio, db_session):
        return TaskStatus.IN_PROGRESS

    monkeypatch.setattr(subtasks, "check_progress", mock_check_progress)

    response = await update_subtask(
        subtask_schema, subtask.subtask_id, subtask.task_id, current_user, mock_db
    )

    assert response.message == "サブタスクを更新しました"
    assert task.progress_ratio == 50
    assert task.task_progress == TaskStatus.IN_PROGRESS
    assert task.changed_time > datetime(2026, 8, 16, tzinfo=timezone.utc)
    mock_db.flush.assert_awaited_once()
    mock_db.commit.assert_awaited_once()


@pytest.mark.anyio
async def test_update_none_task(subtask_schema, subtask, monkeypatch):
    mock_db = AsyncMock()
    current_user = MagicMock()
    current_user.user_id = uuid.uuid4()

    async def mock_fetch_none_task(task_id, user_id, db_session):
        return None

    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_none_task)

    with pytest.raises(HTTPException) as exc_info:
        await update_subtask(
            subtask_schema, subtask.subtask_id, subtask.task_id, current_user, mock_db
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "指定されたタスクが存在しません"


@pytest.mark.anyio
async def test_update_none_subtask(subtask_schema, task, subtask, monkeypatch):
    mock_db = AsyncMock()
    current_user = MagicMock()
    current_user.user_id = uuid.uuid4()

    async def mock_fetch_task(task_id, user_id, db_session):
        return task

    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)

    async def mock_fetch_none_subtask(subtask_id, user_id, db_session):
        return None

    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_none_subtask)

    with pytest.raises(HTTPException) as exc_info:
        await update_subtask(
            subtask_schema, subtask.subtask_id, subtask.task_id, current_user, mock_db
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "指定されたサブタスクが存在しません"


@pytest.mark.anyio
async def test_update_other_task(subtask_schema, task, subtask, other_task, monkeypatch):
    mock_db = AsyncMock()
    current_user = MagicMock()
    current_user.user_id = uuid.uuid4()

    async def mock_fetch_task(task_id, user_id, db_session):
        return task

    monkeypatch.setattr(subtasks, "fetch_task", mock_fetch_task)

    async def mock_fetch_none_subtask(subtask_id, user_id, db_session):
        return subtask

    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_none_subtask)

    with pytest.raises(HTTPException) as exc_info:
        await update_subtask(
            subtask_schema,
            subtask.subtask_id,
            other_task.task_id,
            current_user,
            mock_db,
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "親タスクが異なります"
