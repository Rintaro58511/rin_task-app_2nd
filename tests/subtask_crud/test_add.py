import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from cruds.subtasks import add_subtask


@pytest.mark.anyio
async def test_add_subtask(subtask_schema):
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

    task_id = uuid.uuid4()

    await add_subtask(subtask_schema, task_id, mock_db)

    mock_db.add.assert_called_once()
    assert mock_db.add.call_args.args[0].subtask_name == "test_subtask2"
    assert mock_db.add.call_args.args[0].is_complete is True
    assert mock_db.add.call_args.args[0].task_id == task_id
