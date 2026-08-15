from unittest.mock import AsyncMock

import pytest
from datetime import datetime
import uuid

from models.subtasks import SubTask

from routers.subtasks import get_subtasks
from routers import subtasks

@pytest.fixture
def subtask_list():
    subtask_id1 = uuid.uuid4()
    subtask_id2 = uuid.uuid4()
    task_id = uuid.uuid4()
    expected_subtasks = [
        SubTask(
            subtask_id = subtask_id1,
            task_id = task_id,
            subtask_name = "test_subtask1",
            is_complete = True,
            created_at = datetime(2026, 8, 15)
        ),
        SubTask(
            subtask_id = subtask_id2,
            task_id = task_id,
            subtask_name = "test_subtask2",
            is_complete = False,
            created_at = datetime(2026, 8, 16)
        ),
    ]
    return expected_subtasks

@pytest.mark.anyio
async def test_get_tasks(subtask_list, monkeypatch):
    mock_db = AsyncMock()

    async def mock_fetch_subtasks(task_id, mock_db):
        return subtask_list
    monkeypatch.setattr(subtasks, "fetch_subtasks", mock_fetch_subtasks)

    response = await get_subtasks(subtask_list[0].task_id, mock_db)

    assert response[0].subtask_name == "test_subtask1"
    assert response[0].is_complete == True
    assert response[0].created_at == datetime(2026, 8, 15)
    assert response[1].task_id == response[0].task_id
    assert response[1].subtask_name == "test_subtask2"
    assert response[1].is_complete == False
    assert response[1].created_at == datetime(2026, 8, 16)
    assert len(response) == 2