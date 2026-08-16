from unittest.mock import AsyncMock, MagicMock
import pytest

from datetime import datetime

from cruds.subtasks import fetch_subtasks

@pytest.mark.anyio
async def test_fetch_subtasks(subtask_list):
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_db.execute.return_value = mock_result

    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.all.return_value = subtask_list

    retrieved_subtasks = await fetch_subtasks(subtask_list[0].task_id, mock_db)

    assert len(retrieved_subtasks) == 2

    assert retrieved_subtasks[0].subtask_id == subtask_list[0].subtask_id
    assert retrieved_subtasks[0].subtask_name == "test_subtask1"
    assert retrieved_subtasks[0].is_complete == True
    assert retrieved_subtasks[0].created_at == datetime(2026, 8, 15)

    assert retrieved_subtasks[1].subtask_id == subtask_list[1].subtask_id
    assert retrieved_subtasks[1].subtask_name == "test_subtask2"
    assert retrieved_subtasks[1].is_complete == False
    assert retrieved_subtasks[1].created_at == datetime(2026, 8, 16)
