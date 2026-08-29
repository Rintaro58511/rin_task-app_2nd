from datetime import datetime

import pytest

from cruds.subtasks import modify_subtask


@pytest.mark.anyio
async def test_modify_subtask(subtask_schema, subtask):

    assert subtask.subtask_name == "test_subtask"
    assert subtask.is_complete is False
    assert subtask.created_at == datetime(2026, 8, 15)

    await modify_subtask(subtask_schema, subtask)

    assert subtask.subtask_name == "test_subtask2"
    assert subtask.is_complete is True
    assert subtask.created_at == datetime(2026, 8, 15)
