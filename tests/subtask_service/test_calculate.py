from unittest.mock import AsyncMock
import pytest
import uuid
from datetime import datetime

from service.subtasks import calculate_ratio, fetch_subtasks
from service import subtasks

from models.subtasks import SubTask

@pytest.fixture(scope="module")
def subtask_list_half():
    task_id = uuid.uuid4()
    subtask_id_1 = uuid.uuid4()
    subtask_id_2 = uuid.uuid4()
    expected_subtasks = [
        SubTask(
            subtask_id=subtask_id_1,
            task_id=task_id,
            subtask_name="test_subtask1",
            is_complete=True,
            created_at=datetime(2026, 8, 15)
        ),
        SubTask(
            subtask_id=subtask_id_2,
            task_id=task_id,
            subtask_name="test_subtask2",
            is_complete=False,
            created_at=datetime(2026, 8, 16)
        )
    ]
    return expected_subtasks

@pytest.fixture(scope="module")
def subtask_list_zero():
    task_id = uuid.uuid4()
    subtask_id_1 = uuid.uuid4()
    subtask_id_2 = uuid.uuid4()
    expected_subtasks = [
        SubTask(
            subtask_id=subtask_id_1,
            task_id=task_id,
            subtask_name="test_subtask1",
            is_complete=False,
            created_at=datetime(2026, 8, 15)
        ),
        SubTask(
            subtask_id=subtask_id_2,
            task_id=task_id,
            subtask_name="test_subtask2",
            is_complete=False,
            created_at=datetime(2026, 8, 16)
        )
    ]
    return expected_subtasks

@pytest.fixture(scope="module")
def subtask_list_all():
    task_id = uuid.uuid4()
    subtask_id_1 = uuid.uuid4()
    subtask_id_2 = uuid.uuid4()
    expected_subtasks = [
        SubTask(
            subtask_id=subtask_id_1,
            task_id=task_id,
            subtask_name="test_subtask1",
            is_complete=True,
            created_at=datetime(2026, 8, 15)
        ),
        SubTask(
            subtask_id=subtask_id_2,
            task_id=task_id,
            subtask_name="test_subtask2",
            is_complete=True,
            created_at=datetime(2026, 8, 16)
        )
    ]
    return expected_subtasks

@pytest.mark.anyio
async def test_calculate_ratio(subtask_list_half, subtask_list_zero, subtask_list_all, monkeypatch):
    user_id = uuid.uuid4()
    async def mock_fetch_subtasks_half(subtask_id, user_id, db_session):
        return subtask_list_half

    monkeypatch.setattr(subtasks, "fetch_subtasks", mock_fetch_subtasks_half)
    mock_db_half = AsyncMock()
    test_progress_ratio_half = await calculate_ratio(subtask_list_half[0].task_id, user_id, mock_db_half)
    assert test_progress_ratio_half == 50

    async def mock_fetch_subtasks_all(subtask_id, user_id, db_session):
        return subtask_list_all
    
    monkeypatch.setattr(subtasks, "fetch_subtasks", mock_fetch_subtasks_all)
    mock_db_all = AsyncMock()
    test_progress_ratio_all = await calculate_ratio(subtask_list_all[0].task_id, user_id, mock_db_all)
    assert test_progress_ratio_all == 100

    async def mock_fetch_subtasks_zero(subtask_id, user_id, db_session):
        return subtask_list_zero
        
    monkeypatch.setattr(subtasks, "fetch_subtasks", mock_fetch_subtasks_zero)
    mock_db_zero = AsyncMock()
    test_progress_ratio_zero = await calculate_ratio(subtask_list_zero[0].task_id, user_id, mock_db_zero)
    assert test_progress_ratio_zero == 0


@pytest.mark.anyio
async def test_none_calculate_ratio(monkeypatch):
    user_id = uuid.uuid4()
    async def mock_fetch_subtasks(subtask_id, user_id, db_session):
        return []

    mock_task_id = uuid.uuid4()

    monkeypatch.setattr(subtasks, "fetch_subtasks", mock_fetch_subtasks)

    mock_db = AsyncMock()

    test_progress_ratio = await calculate_ratio(mock_task_id, user_id, mock_db)

    assert test_progress_ratio is None