from unittest.mock import AsyncMock, MagicMock
import pytest

import uuid
from datetime import datetime, date

from cruds import tasks
from cruds.tasks import fetch_task, fetch_tasks, add_task, remove_task, modify_task
from models.tasks import Task
from schemas.tasks import TaskSchema, TaskStatusSchema, UpdateAndCreateTaskSchema
from enums import TaskStatus


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


@pytest.mark.anyio
async def test_fetch_tasks():
    mock_db = AsyncMock()

    user_id = uuid.uuid4()

    expected_tasks = [
        Task(
            task_id=uuid.uuid4(),
            task_name="test_task",
            task_deadline=date(2026, 8, 1),
            task_detail="コードのリファクタリング",
            changed_time=datetime(2026, 7, 30, 11, 11, 11),
            user=None,
            user_id=user_id,
            task_progress=TaskStatus.IN_PROGRESS,
            progress_ratio=90,
            progress_comment="終わりそう",
        ),
        Task(
            task_id=uuid.uuid4(),
            task_name="test_task2",
            task_deadline=date(2026, 8, 2),
            task_detail="コードのリファクタリング",
            changed_time=datetime(2026, 7, 30, 11, 11, 12),
            user=None,
            user_id=user_id,
            task_progress=TaskStatus.IN_PROGRESS,
            progress_ratio=90,
            progress_comment="終わりそう",
        ),
    ]

    mock_results = MagicMock()
    mock_db.execute.return_value = mock_results

    mock_scalars = MagicMock()
    mock_results.scalars.return_value = mock_scalars
    mock_scalars.all.return_value = expected_tasks

    retrieved_tasks = await fetch_tasks(mock_db, user_id)

    assert retrieved_tasks[0].task_name == "test_task"
    assert retrieved_tasks[1].task_name == "test_task2"
    assert retrieved_tasks[0].task_deadline == date(2026, 8, 1)
    assert retrieved_tasks[1].task_deadline == date(2026, 8, 2)
    assert retrieved_tasks[0].changed_time == datetime(2026, 7, 30, 11, 11, 11)
    assert retrieved_tasks[1].changed_time == datetime(2026, 7, 30, 11, 11, 12)


@pytest.mark.anyio
async def test_add_task():
    mock_db = AsyncMock()

    user_id = uuid.uuid4()

    status_data = TaskStatusSchema(
        task_progress=TaskStatus.IN_PROGRESS,
        progress_ratio=90,
        progress_comment="終わりそう",
    )

    expected_task = UpdateAndCreateTaskSchema(
        task_name="test_task2",
        task_deadline=date(2026, 8, 2),
        task_detail="コードのリファクタリング",
        changed_time=datetime(2026, 7, 30, 11, 11, 12),
        task_status=status_data,
    )

    returned_task = await add_task(expected_task, mock_db, user_id)

    assert returned_task.task_name == "test_task2"
    assert returned_task.user_id == user_id
    assert returned_task.task_progress == TaskStatus.IN_PROGRESS
    assert returned_task.progress_ratio == 90

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.anyio
async def test_remove_task(monkeypatch):
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

    async def mock_fetch_task(mock_task_id, mock_db):
        return expected_task

    monkeypatch.setattr(tasks, "fetch_task", mock_fetch_task)

    await remove_task(task_id, mock_db)

    mock_db.delete.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.anyio
async def test_modify_task():
    mock_db = AsyncMock()

    task_id = uuid.uuid4()
    user_id = uuid.uuid4()
    target_task = Task(
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

    assert target_task.task_name == "test_task"
    assert target_task.task_deadline == date(2026, 8, 1)
    assert target_task.task_progress == TaskStatus.IN_PROGRESS
    assert target_task.progress_ratio == 90
    assert target_task.progress_comment == "終わりそう"

    status_data = TaskStatusSchema(
        task_progress=TaskStatus.DONE,
        progress_ratio=100,
        progress_comment="終わった",
    )

    expected_task = UpdateAndCreateTaskSchema(
        task_name="test_task2",
        task_deadline=date(2026, 8, 2),
        task_detail="コードのリファクタリング",
        changed_time=datetime(2026, 7, 30, 11, 11, 12),
        task_status=status_data,
    )

    returned_task = await modify_task(expected_task, target_task, mock_db)

    assert returned_task.task_name == "test_task2"
    assert returned_task.task_deadline == date(2026, 8, 2)
    assert returned_task.task_progress == TaskStatus.DONE
    assert returned_task.progress_ratio == 100
    assert returned_task.progress_comment == "終わった"

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


# async def modify_task(
#     task: UpdateAndCreateTaskSchema, target_task: Task, db_session: AsyncSession
# ) -> Task:

#     target_task.task_name = task.task_name
#     target_task.task_deadline = task.task_deadline
#     target_task.task_detail = task.task_detail
#     target_task.changed_itme = task.changed_time
#     target_task.task_progress = task.task_status.task_progress
#     target_task.progress_ratio = task.task_status.progress_ratio
#     target_task.progress_comment = task.task_status.progress_comment

#     await db_session.commit()
#     await db_session.refresh(target_task)

#     return target_task
