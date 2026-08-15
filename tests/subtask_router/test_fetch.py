import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock
from fastapi import HTTPException

from models.subtasks import SubTask

from routers.subtasks import search_subtask
from routers import subtasks


@pytest.fixture
def subtask():
    expected_subtask = SubTask(
        subtask_id = uuid.uuid4(),
        task_id = uuid.uuid4(),
        subtask_name = "test_subtask",
        is_complete = True,
        created_at = datetime(2026, 8, 15)
    )
    return expected_subtask

@pytest.mark.anyio
async def test_search_subtask(subtask, monkeypatch):
    mock_db = AsyncMock()
    subtask_id = uuid.uuid4()

    async def mock_fetch_subtask(subtask_id, db_session):
        return subtask
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)

    response = await search_subtask(subtask_id, mock_db)

    assert response.subtask_name == "test_subtask"
    assert response.is_complete == True
    assert response.created_at == datetime(2026, 8, 15)

@pytest.mark.anyio
async def test_search_none_subtask(subtask, monkeypatch):
    mock_db = AsyncMock()

    async def mock_fetch_subtask(subtask_id, mock_db):
        return None
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)

    with pytest.raises(HTTPException) as exc_info:
        await search_subtask(subtask.subtask_id, mock_db)

    assert exc_info.value.detail == "指定されたサブタスクが見つかりません"
    assert exc_info.value.status_code == 404
