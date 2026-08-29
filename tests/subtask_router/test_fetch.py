import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status

from routers import subtasks
from routers.subtasks import search_subtask


@pytest.mark.anyio
async def test_search_subtask(subtask, monkeypatch):
    mock_db = AsyncMock()
    subtask_id = uuid.uuid4()
    current_user = MagicMock()
    current_user.user_id = uuid.uuid4()

    async def mock_fetch_subtask(subtask_id, user_id, db_session):
        return subtask
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)

    response = await search_subtask(subtask_id, current_user, mock_db)

    assert response.subtask_name == "test_subtask"
    assert response.is_complete is False
    assert response.created_at == datetime(2026, 8, 15)

@pytest.mark.anyio
async def test_search_none_subtask(subtask, monkeypatch):
    mock_db = AsyncMock()
    current_user = MagicMock()
    current_user.user_id = uuid.uuid4()

    async def mock_fetch_subtask(subtask_id, user_id, mock_db):
        return None
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)

    with pytest.raises(HTTPException) as exc_info:
        await search_subtask(subtask.subtask_id, current_user, mock_db)

    assert exc_info.value.detail == "指定されたサブタスクが見つかりません"
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
