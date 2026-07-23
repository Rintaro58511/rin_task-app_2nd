from unittest.mock import AsyncMock
import pytest
import routers.user as user
import routers.tasks as task
from httpx import ASGITransport, AsyncClient
from main import app
import uuid
from datetime import datetime, date
from models.tasks import Task
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
async def test_delete_task(monkeypatch, override_get_current_user, override_get_db):
    user_id = uuid.uuid4()
    task_id = uuid.uuid4()

    async def mock_current_user():
        mock_user = AsyncMock()
        mock_user.user_id = user_id
        yield mock_user

    app.dependency_overrides[user.get_current_user] = mock_current_user

    async def mock_fetch_task(task_id, db):
        return Task(
            task_id=task_id,
            task_name="test_task",
            task_deadline=date(2026, 8, 1),
            task_detail="コードのリファクタリング",
            changed_time=datetime(2026, 7, 30, 11, 11, 11),
            user_id=user_id,
            user=None,
            task_progress="DONE",
            progress_ratio=100,
            progress_comment="終わった",
        )

    monkeypatch.setattr(task, "fetch_task", mock_fetch_task)

    async def mock_remove_task(task_id, db):
        return True

    monkeypatch.setattr(task, "remove_task", mock_remove_task)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.delete(
            f"/tasks/{task_id}",
        )
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "タスクを削除しました"
