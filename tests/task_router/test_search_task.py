from unittest.mock import AsyncMock, MagicMock
import pytest
import routers.user as user
import routers.tasks as task
from httpx import ASGITransport, AsyncClient
from main import app
import uuid
from datetime import datetime, date
from models.tasks import Task
from schemas.tasks import TaskSchema, TaskStatusSchema, UpdateAndCreateTaskSchema
from enums import TaskStatus
from fastapi import status
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
async def test_search_task(monkeypatch, override_get_db, override_get_current_user):
    dummy_user_id = uuid.uuid4()
    dummy_task_id = uuid.uuid4()

    async def mock_current_user():
        mock_user = AsyncMock()
        mock_user.user_id = dummy_user_id
        yield mock_user

    app.dependency_overrides[user.get_current_user] = mock_current_user

    async def mock_fetch_task(task_id, db):

        target_task = Task(
            task_id=task_id,
            task_name="test_task",
            task_deadline=date(2026, 8, 1),
            task_detail="コードのリファクタリング",
            changed_time=datetime(2026, 7, 30, 11, 11, 11),
            user=None,
            user_id=dummy_user_id,
            task_progress=TaskStatus.IN_PROGRESS,
            progress_ratio=90,
            progress_comment="終わりそう",
        )

        return target_task

    monkeypatch.setattr(task, "fetch_task", mock_fetch_task)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/tasks/{dummy_task_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["task_name"] == "test_task"
    assert body["task_deadline"] == "2026-08-01"
    assert body["task_status"]["progress_comment"] == "終わりそう"


@pytest.mark.anyio
async def test_fail_fetch_task(monkeypatch, override_get_db, override_get_current_user):
    dummy_task_id = uuid.uuid4()

    async def mock_fail_fetch_task(task_id, db):
        return None

    monkeypatch.setattr(task, "fetch_task", mock_fail_fetch_task)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(f"/tasks/{dummy_task_id}")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "指定されたタスクが見つかりません。"


@pytest.mark.anyio
async def test_fail_db_create_task(
    monkeypatch, override_get_db, override_get_current_user
):
    dummy_user_id = uuid.uuid4()
    dummy_task_id = uuid.uuid4()

    # 1. 認証ユーザーのIDを設定
    async def mock_current_user():
        mock_user = AsyncMock()
        mock_user.user_id = dummy_user_id
        yield mock_user

    app.dependency_overrides[user.get_current_user] = mock_current_user

    async def mock_fetch_another_user_task(task_id, db):
        return Task(
            task_id=task_id,
            task_name="test_task",
            task_deadline=date(2026, 8, 1),
            task_detail="コードのリファクタリング",
            changed_time=datetime(2026, 7, 30, 11, 11, 11),
            user=None,
            user_id=uuid.uuid4(),
            task_progress=TaskStatus.IN_PROGRESS,
            progress_ratio=90,
            progress_comment="終わりそう",
        )

    monkeypatch.setattr(task, "fetch_task", mock_fetch_another_user_task)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/tasks/{dummy_task_id}",
        )
    assert response.status_code == 403
    body = response.json()
    assert body["detail"] == "他ユーザーのタスクです。"
