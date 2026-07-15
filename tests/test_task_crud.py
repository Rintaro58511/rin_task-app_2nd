from unittest.mock import AsyncMock, MagicMock
import pytest

import uuid
from datetime import datetime, date

from cruds import tasks
from cruds.tasks import fetch_task, add_task
from models.tasks import Task
from schemas.tasks import TaskSchema, TaskStatus


@pytest.mark.anyio
async def test_fetch_task():
    mock_db = AsyncMock()

    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    expected_task = Task(
        task_id=task_id,
        task_name="test_task",
        task_deadline=date(2026, 8, 1),
        task_detail="コードのリファクタリング",
        changed_time=datetime(2026, 7, 30, 11, 11, 11),
        user=None,
        user_id=user_id,
        task_progress=TaskStatus.IN_PROGRESS,
        progress_ratio=90,
        progress_comment="終わりそう",
    )

    mock_result = MagicMock()
    mock_db.execute.return_value = mock_result

    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.first.return_value = expected_task

    retrieved_task = await fetch_task(task_id, mock_db)

    assert retrieved_task.task_name == "test_task"
    assert retrieved_task.task_deadline == date(2026, 8, 1)
    assert retrieved_task.task_detail == "コードのリファクタリング"
    assert retrieved_task.task_progress == TaskStatus.IN_PROGRESS

    mock_db.execute.assert_called_once()


# async def fetch_task(task_id: UUID, db_session: AsyncSession) -> Task:
#     result = await db_session.execute(select(Task).filter(Task.task_id == task_id))
#     target_task = result.scalars().first()

#     return target_task
