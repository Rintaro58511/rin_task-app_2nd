from models.subtasks import SubTask
from models.tasks import Task
from models.user import User
import pytest
import uuid
from datetime import datetime, date
from enums import TaskStatus
from schemas.subtasks import UpdateAndCreateSubTaskSchema

@pytest.fixture
def subtask():
    expected_subtask = SubTask(
        subtask_id = uuid.uuid4(),
        task_id = uuid.uuid4(),
        subtask_name = "test_subtask",
        is_complete = False,
        created_at = datetime(2026, 8, 15)
    )
    return expected_subtask

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

@pytest.fixture
def subtask_schema():
    expeted_subtask_schema = UpdateAndCreateSubTaskSchema(
        subtask_name = "test_subtask2",
        is_complete = True,
    )
    return expeted_subtask_schema

@pytest.fixture
def task(subtask):
    expeted_task = Task(
        task_id = subtask.task_id,
        user_id = uuid.uuid4(),
        task_name = "test_task",
        task_deadline = date(2026, 9, 20),
        task_detail = None,
        changed_time = datetime(2026, 8, 16),
        task_progress = TaskStatus.TODO,
        progress_ratio = 80,
        progress_comment = "少し進んだ"
    )
    return expeted_task

@pytest.fixture
def other_task():
    expeted_task = Task(
        task_id = uuid.uuid4(),
        user_id = uuid.uuid4(),
        task_name = "test_task",
        task_deadline = date(2026, 9, 20),
        task_detail = None,
        changed_time = datetime(2026, 8, 16),
        task_progress = TaskStatus.TODO,
        progress_ratio = 10,
        progress_comment = "少し進んだ"
    )
    return expeted_task
