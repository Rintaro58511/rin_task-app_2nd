from unittest.mock import AsyncMock, MagicMock
import pytest

import uuid
from datetime import datetime

from cruds.subtasks import fetch_subtask
from models.subtasks import SubTask

@pytest.fixture
def subtask():
    subtask_id = uuid.uuid4()
    task_id = uuid.uuid4()
    expected_subtask = SubTask(
        subtask_id=subtask_id,
        task_id=task_id,
        subtask_name="test_subtask",
        is_complete=True,
        created_at=datetime(2026, 8, 15)
    )
    return expected_subtask

@pytest.mark.anyio
async def test_fetch_subtask(subtask):
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_db.execute.return_value = mock_result

    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.first.return_value = subtask

    retrieved_subtask = await fetch_subtask(subtask.subtask_id, mock_db)

    assert retrieved_subtask.subtask_name == "test_subtask"
    assert retrieved_subtask.is_complete == True
    assert retrieved_subtask.created_at == datetime(2026, 8, 15)

    mock_db.execute.assert_called_once()
