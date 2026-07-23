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
async def test_create_task(monkeypatch, override_get_current_user, override_get_db):
    async def mock_add_task(task, user_id, db):
        status = TaskStatusSchema(
            task_progress=TaskStatus.IN_PROGRESS,
            progress_ratio=90,
            progress_comment="終わりそう",
        )
        return UpdateAndCreateTaskSchema(
            task_name="test_task",
            task_deadline=date(2026, 8, 1),
            task_detail="コードのリファクタリング",
            changed_time=datetime(2026, 7, 30, 11, 11, 11),
            task_status=status,
        )

    monkeypatch.setattr(task, "add_task", mock_add_task)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/tasks",
            json={
                "task_name": "test_task",
                "task_deadline": "2026-08-01",
                "task_detail": "コードのリファクタリング",
                "changed_time": "2026-07-30T11:11:11",
                "task_status": {
                    "task_progress": "IN_PROGRESS",
                    "progress_ratio": 90,
                    "progress_comment": "終わりそう",
                },
            },
        )
    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "タスク追加ができました"


@pytest.mark.anyio
async def test_fail_create_task(
    monkeypatch, override_get_current_user, override_get_db
):
    async def mock_fail_add_task(task, user_id, db):
        status = TaskStatusSchema(
            task_progress=TaskStatus.IN_PROGRESS,
            progress_ratio=90,
            progress_comment="終わりそう",
        )
        return UpdateAndCreateTaskSchema(
            task_name="test_task",
            task_deadline=date(2026, 6, 1),
            task_detail="コードのリファクタリング",
            changed_time=datetime(2026, 7, 30, 11, 11, 11),
            task_status=status,
        )

    monkeypatch.setattr(task, "add_task", mock_fail_add_task)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/tasks",
            json={
                "task_name": "test_task",
                "task_deadline": "2026-06-01",
                "task_detail": "コードのリファクタリング",
                "changed_time": "2026-07-30T11:11:11",
                "task_status": {
                    "task_progress": "IN_PROGRESS",
                    "progress_ratio": 90,
                    "progress_comment": "終わりそう",
                },
            },
        )
    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "期限が過去の日付になっています"


@pytest.mark.anyio
async def test_fail_db_create_task(
    monkeypatch, override_get_current_user, override_get_db
):
    async def mock_fail_db_add_task(task, user_id, db):
        raise Exception("データベースエラーのテスト")

    monkeypatch.setattr(task, "add_task", mock_fail_db_add_task)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/tasks",
            json={
                "task_name": "test_task",
                "task_deadline": "2026-08-01",
                "task_detail": "コードのリファクタリング",
                "changed_time": "2026-07-30T11:11:11",
                "task_status": {
                    "task_progress": "IN_PROGRESS",
                    "progress_ratio": 90,
                    "progress_comment": "終わりそう",
                },
            },
        )
    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "タスクの登録に失敗しました"
