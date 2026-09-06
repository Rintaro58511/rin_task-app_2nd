import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from routers import subtasks
from routers.subtasks import get_subtasks


@pytest.mark.anyio
async def test_get_tasks(subtask_list, monkeypatch):
    mock_db = AsyncMock()
    current_user = MagicMock()
    current_user.user_id = uuid.uuid4()

    async def mock_fetch_subtasks(task_id, current_user, mock_db):
        return subtask_list

    monkeypatch.setattr(subtasks, "fetch_subtasks", mock_fetch_subtasks)

    response = await get_subtasks(subtask_list[0].task_id, mock_db)

    assert response[0].subtask_name == "test_subtask1"
    assert response[0].is_complete is True
    assert response[0].created_at == datetime(2026, 8, 15)
    assert response[1].task_id == response[0].task_id
    assert response[1].subtask_name == "test_subtask2"
    assert response[1].is_complete is False
    assert response[1].created_at == datetime(2026, 8, 16)
    assert len(response) == 2
