import pytest
import uuid
from datetime import datetime

from cruds.subtasks import modify_subtask

from schemas.subtasks import UpdateAndCreateSubTaskSchema

from models.subtasks import SubTask

@pytest.mark.anyio
async def test_modify_subtask(subtask_schema, subtask):

    assert subtask.subtask_name == "test_subtask"
    assert subtask.is_complete == False
    assert subtask.created_at == datetime(2026, 8, 15)
    
    await modify_subtask(subtask_schema, subtask)

    assert subtask.subtask_name == "test_subtask2"
    assert subtask.is_complete == True
    assert subtask.created_at == datetime(2026, 8, 15)
