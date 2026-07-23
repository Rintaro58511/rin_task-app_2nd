from unittest.mock import AsyncMock, MagicMock
import pytest
import routers.user as user
import routers.tasks as task
from httpx import ASGITransport, AsyncClient
from main import app
import uuid
from datetime import datetime, date
from models.tasks import Task
from enums import TaskStatus
import db


@pytest.fixture
def override_get_current_user():

    async def override_user():
        yield AsyncMock()

    app.dependency_overrides[user.get_current_user] = override_user

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def override_get_db():

    async def override_db():
        yield AsyncMock()

    app.dependency_overrides[db.get_db_session] = override_db

    yield

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_get_row_tasks(monkeypatch, override_get_current_user, override_get_db):
    async def mock_fetch_tasks(user_id, db):
        mock_tasks = [
            Task(
                task_id=uuid.uuid4(),
                task_name="test_task",
                task_deadline=date(2026, 8, 4),
                task_detail="コードのリファクタリング",
                changed_time=datetime.now(),
                user=None,
                user_id=user_id,
                task_progress=TaskStatus.TODO,
                progress_ratio=0,
                progress_comment="未着手",
            ),
            Task(
                task_id=uuid.uuid4(),
                task_name="test_task2",
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
                task_name="test_task3",
                task_deadline=date(2026, 8, 2),
                task_detail="コードのリファクタリング",
                changed_time=datetime(2026, 7, 30, 11, 11, 12),
                user=None,
                user_id=user_id,
                task_progress=TaskStatus.DONE,
                progress_ratio=100,
                progress_comment="終わった",
            ),
        ]

        return mock_tasks

    monkeypatch.setattr(task, "fetch_tasks", mock_fetch_tasks)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/tasks")
    assert response.status_code == 200
    body = response.json()
    assert body[0]["task_name"] == "test_task"
    assert body[1]["task_name"] == "test_task2"
    assert body[2]["task_name"] == "test_task3"
    assert body[0]["task_status"]["task_progress"] == "TODO"
    assert body[1]["task_status"]["task_progress"] == "IN_PROGRESS"
    assert body[2]["task_status"]["task_progress"] == "DONE"


@pytest.mark.anyio
async def test_get_sorted_deadline_tasks(
    monkeypatch, override_get_current_user, override_get_db
):
    async def mock_arrange_tasks(sort, user_id, db):
        mock_tasks = [
            Task(
                task_id=uuid.uuid4(),
                task_name="test_task2",
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
                task_name="test_task3",
                task_deadline=date(2026, 8, 2),
                task_detail="コードのリファクタリング",
                changed_time=datetime(2026, 7, 30, 11, 11, 12),
                user=None,
                user_id=user_id,
                task_progress=TaskStatus.DONE,
                progress_ratio=100,
                progress_comment="終わった",
            ),
            Task(
                task_id=uuid.uuid4(),
                task_name="test_task",
                task_deadline=date(2026, 8, 4),
                task_detail="コードのリファクタリング",
                changed_time=datetime.now(),
                user=None,
                user_id=user_id,
                task_progress=TaskStatus.TODO,
                progress_ratio=0,
                progress_comment="未着手",
            ),
        ]

        return mock_tasks

    monkeypatch.setattr(task, "arrange_tasks", mock_arrange_tasks)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/tasks", params={"sort": "deadline"})
    assert response.status_code == 200
    body = response.json()
    assert body[0]["task_name"] == "test_task2"
    assert body[1]["task_name"] == "test_task3"
    assert body[2]["task_name"] == "test_task"
    assert body[0]["task_status"]["task_progress"] == "IN_PROGRESS"
    assert body[1]["task_status"]["task_progress"] == "DONE"
    assert body[2]["task_status"]["task_progress"] == "TODO"


@pytest.mark.anyio
async def test_get_sorted_status_tasks(
    monkeypatch, override_get_current_user, override_get_db
):
    async def mock_arrange_tasks(sort, user_id, db):
        mock_tasks = [
            Task(
                task_id=uuid.uuid4(),
                task_name="test_task",
                task_deadline=date(2026, 8, 4),
                task_detail="コードのリファクタリング",
                changed_time=datetime.now(),
                user=None,
                user_id=user_id,
                task_progress=TaskStatus.TODO,
                progress_ratio=0,
                progress_comment="未着手",
            ),
            Task(
                task_id=uuid.uuid4(),
                task_name="test_task2",
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
                task_name="test_task3",
                task_deadline=date(2026, 8, 2),
                task_detail="コードのリファクタリング",
                changed_time=datetime(2026, 7, 30, 11, 11, 12),
                user=None,
                user_id=user_id,
                task_progress=TaskStatus.DONE,
                progress_ratio=100,
                progress_comment="終わった",
            ),
        ]

        return mock_tasks

    monkeypatch.setattr(task, "arrange_tasks", mock_arrange_tasks)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/tasks", params={"sort": "status"})
    assert response.status_code == 200
    body = response.json()
    assert body[0]["task_name"] == "test_task"
    assert body[1]["task_name"] == "test_task2"
    assert body[2]["task_name"] == "test_task3"
    assert body[0]["task_status"]["task_progress"] == "TODO"
    assert body[1]["task_status"]["task_progress"] == "IN_PROGRESS"
    assert body[2]["task_status"]["task_progress"] == "DONE"


@pytest.mark.anyio
async def test_get_filtered_tasks(
    monkeypatch, override_get_current_user, override_get_db
):
    async def mock_filter_tasks(search_name, user_id, db):
        mock_tasks = [
            Task(
                task_id=uuid.uuid4(),
                task_name="python",
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
                task_name="python_fastapi",
                task_deadline=date(2026, 8, 2),
                task_detail="コードのリファクタリング",
                changed_time=datetime(2026, 7, 30, 11, 11, 12),
                user=None,
                user_id=user_id,
                task_progress=TaskStatus.DONE,
                progress_ratio=100,
                progress_comment="終わった",
            ),
            Task(
                task_id=uuid.uuid4(),
                task_name="java",
                task_deadline=date(2026, 8, 4),
                task_detail="コードのリファクタリング",
                changed_time=datetime.now(),
                user=None,
                user_id=user_id,
                task_progress=TaskStatus.TODO,
                progress_ratio=0,
                progress_comment="未着手",
            ),
        ]

        return mock_tasks[0:2]

    monkeypatch.setattr(task, "filter_tasks", mock_filter_tasks)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/tasks", params={"search_name": "python"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["task_name"] == "python"
    assert body[1]["task_name"] == "python_fastapi"
    assert body[0]["task_status"]["task_progress"] == "IN_PROGRESS"
    assert body[1]["task_status"]["task_progress"] == "DONE"
