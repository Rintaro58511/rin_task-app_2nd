import uuid
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from cruds import tasks
from cruds.tasks import (
    add_task,
    arrange_tasks,
    fetch_task,
    fetch_tasks,
    filter_tasks,
    modify_task,
    remove_task,
)
from enums import TaskStatus
from models.tasks import Task
from schemas.tasks import TaskStatusSchema, UpdateAndCreateTaskSchema


@pytest.mark.asyncio
async def test_fetch_task(test_task):
    mock_db = AsyncMock()

    mock_result = MagicMock()
    mock_db.execute.return_value = mock_result

    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_scalars.first.return_value = test_task

    retrieved_task = await fetch_task(test_task.task_id, test_task.user_id, mock_db)

    assert retrieved_task.task_name == "test_task"
    assert retrieved_task.task_deadline == date(2026, 9, 20)
    assert retrieved_task.task_progress == TaskStatus.IN_PROGRESS

    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
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

    retrieved_tasks = await fetch_tasks(user_id, mock_db)

    assert retrieved_tasks[0].task_name == "test_task"
    assert retrieved_tasks[1].task_name == "test_task2"
    assert retrieved_tasks[0].task_deadline == date(2026, 8, 1)
    assert retrieved_tasks[1].task_deadline == date(2026, 8, 2)
    assert retrieved_tasks[0].changed_time == datetime(2026, 7, 30, 11, 11, 11)
    assert retrieved_tasks[1].changed_time == datetime(2026, 7, 30, 11, 11, 12)


@pytest.mark.asyncio
async def test_add_task():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()

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

    await add_task(expected_task, user_id, mock_db)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_remove_task(monkeypatch, test_task):
    mock_db = AsyncMock()

    await remove_task(test_task, mock_db)

    mock_db.delete.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_modify_task(test_task):
    mock_db = AsyncMock()

    assert test_task.task_name == "test_task"
    assert test_task.task_deadline == date(2026, 9, 20)
    assert test_task.task_progress == TaskStatus.IN_PROGRESS
    assert test_task.progress_ratio == 80
    assert test_task.progress_comment == "少し進んだ"

    status_data = TaskStatusSchema(
        task_progress=TaskStatus.DONE,
        progress_ratio=100,
        progress_comment="終わった",
    )

    expected_task = UpdateAndCreateTaskSchema(
        task_name="test_task2",
        task_deadline=date(2026, 12, 2),
        task_detail="コードのリファクタリング",
        changed_time=datetime(2026, 7, 30, 11, 11, 12),
        task_status=status_data,
    )

    returned_task = await modify_task(expected_task, test_task, mock_db)

    assert returned_task.task_name == "test_task2"
    assert returned_task.task_deadline == date(2026, 12, 2)
    assert returned_task.task_progress == TaskStatus.DONE
    assert returned_task.progress_ratio == 100
    assert returned_task.progress_comment == "終わった"

    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_arrange_tasks():

    mock_db = AsyncMock()
    user_id = uuid.uuid4()

    mock_results = MagicMock()
    mock_db.execute.return_value = mock_results
    mock_scalars = MagicMock()
    mock_results.scalars.return_value = mock_scalars

    task_done = Task(
        task_id=uuid.uuid4(),
        task_name="test_task2",
        task_deadline=date(2026, 8, 3),
        task_detail="コードのリファクタリング",
        changed_time=datetime(2026, 7, 30, 11, 11, 12),
        user=None,
        user_id=user_id,
        task_progress=TaskStatus.DONE,
        progress_ratio=90,
        progress_comment="終わりそう",
    )
    task_in_progress = Task(
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
    )
    task_todo = Task(
        task_id=uuid.uuid4(),
        task_name="test_task2",
        task_deadline=date(2026, 8, 2),
        task_detail="コードのリファクタリング",
        changed_time=datetime(2026, 7, 30, 11, 11, 12),
        user=None,
        user_id=user_id,
        task_progress=TaskStatus.TODO,
        progress_ratio=90,
        progress_comment="終わりそう",
    )

    mock_scalars.all.return_value = [task_in_progress, task_todo, task_done]

    sort_order = "deadline"
    sorted_by_deadline_tasks = await arrange_tasks(sort_order, user_id, mock_db)

    assert sorted_by_deadline_tasks[0].task_deadline == date(2026, 8, 1)
    assert sorted_by_deadline_tasks[1].task_deadline == date(2026, 8, 2)
    assert sorted_by_deadline_tasks[2].task_deadline == date(2026, 8, 3)

    mock_scalars.all.return_value = [task_todo, task_in_progress, task_done]

    sort_order = "status"
    sorted_by_status_tasks = await arrange_tasks(sort_order, user_id, mock_db)

    assert sorted_by_status_tasks[0].task_progress == TaskStatus.TODO
    assert sorted_by_status_tasks[1].task_progress == TaskStatus.IN_PROGRESS
    assert sorted_by_status_tasks[2].task_progress == TaskStatus.DONE

    assert mock_db.execute.call_count == 2

    assert mock_results.scalars.call_count == 2

    assert mock_scalars.all.call_count == 2


@pytest.mark.asyncio
async def test_filter_tasks():
    mock_db = AsyncMock()

    user_id = uuid.uuid4()

    task_python = Task(
        task_id=uuid.uuid4(),
        task_name="python",
        task_deadline=date(2026, 8, 3),
        task_detail="コードのリファクタリング",
        changed_time=datetime(2026, 7, 30, 11, 11, 12),
        user=None,
        user_id=user_id,
        task_progress=TaskStatus.DONE,
        progress_ratio=90,
        progress_comment="終わりそう",
    )
    task_python_test = Task(
        task_id=uuid.uuid4(),
        task_name="python_test",
        task_deadline=date(2026, 8, 1),
        task_detail="コードのリファクタリング",
        changed_time=datetime(2026, 7, 30, 11, 11, 11),
        user=None,
        user_id=user_id,
        task_progress=TaskStatus.IN_PROGRESS,
        progress_ratio=90,
        progress_comment="終わりそう",
    )

    mock_results = MagicMock()
    mock_db.execute.return_value = mock_results
    mock_scalars = MagicMock()
    mock_results.scalars.return_value = mock_scalars

    mock_scalars.all.return_value = [task_python, task_python_test]

    filtered_tasks = await filter_tasks("python", user_id, mock_db)

    assert len(filtered_tasks) == 2
    assert filtered_tasks[0].task_name == "python"
    assert filtered_tasks[1].task_name == "python_test"

    mock_db.execute.assert_awaited_once()
    mock_results.scalars.assert_called_once()
    mock_scalars.all.assert_called_once()
