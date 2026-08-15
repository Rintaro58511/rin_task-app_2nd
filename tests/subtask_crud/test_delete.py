from unittest.mock import AsyncMock
import pytest
import uuid
from datetime import datetime

from cruds.subtasks import remove_subtask
from cruds import subtasks

from models.subtasks import SubTask

@pytest.fixture(scope="module")
def target_subtask():
    expected_subtask = SubTask(
        subtask_id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        subtask_name="test_subtask",
        is_complete=True,
        created_at=datetime(2026, 8, 15)
    )
    return expected_subtask

@pytest.mark.anyio
async def test_remove_subtask(target_subtask, monkeypatch):
    async def mock_fetch_subtask(subtask_id, db_session):
        return target_subtask

    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)
    
    mock_db = AsyncMock()
    mock_db.delete = AsyncMock()
    
    await remove_subtask(target_subtask.subtask_id, mock_db)

    assert mock_db.delete.call_args.args[0] == target_subtask

    mock_db.delete.assert_called_once()