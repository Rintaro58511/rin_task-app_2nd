from unittest.mock import AsyncMock

import pytest
from cruds.subtasks import remove_subtask


@pytest.mark.anyio
async def test_remove_subtask(subtask, monkeypatch):
    mock_db = AsyncMock()
    mock_db.delete = AsyncMock()

    await remove_subtask(subtask, mock_db)

    assert mock_db.delete.call_args.args[0] == subtask

    mock_db.delete.assert_called_once()
