import pytest
import uuid
from datetime import datetime

from cruds.subtasks import modify_subtask

from schemas.subtasks import UpdateAndCreateSubTaskSchema

from models.subtasks import SubTask

@pytest.fixture(scope="module")
def subtask_schema():
    expected_subtask_schemas = UpdateAndCreateSubTaskSchema(
            subtask_name="test_subtask_update",
            is_complete=True,
        )
    return expected_subtask_schemas

@pytest.fixture(scope="module")
def subtask():
    expected_subtask = SubTask(
            subtask_id=uuid.uuid4(),
            task_id=uuid.uuid4(),
            subtask_name="test_subtask",
            is_complete=False,
            created_at=datetime(2026, 8, 15)
        )
    return expected_subtask

@pytest.mark.anyio
async def test_modify_subtask(subtask_schema, subtask):

    assert subtask.subtask_name == "test_subtask"
    assert subtask.is_complete == False
    assert subtask.created_at == datetime(2026, 8, 15)
    
    await modify_subtask(subtask_schema, subtask)

    assert subtask.subtask_name == "test_subtask_update"
    assert subtask.is_complete == True
    assert subtask.created_at == datetime(2026, 8, 15)
