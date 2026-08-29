from datetime import date, datetime

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

import routers.tasks as task
from enums import TaskStatus
from main import app
from schemas.tasks import TaskStatusSchema, UpdateAndCreateTaskSchema


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

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/tasks",
            json={
                "task_name": "test_task",
                "task_deadline": "2027-08-01",
                "task_detail": "コードのリファクタリング",
                "changed_time": "2026-07-30T11:11:11",
                "task_status": {
                    "task_progress": "IN_PROGRESS",
                    "progress_ratio": 90,
                    "progress_comment": "終わりそう",
                },
            },
        )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["message"] == "タスク追加ができました"


@pytest.mark.anyio
async def test_fail_create_task(monkeypatch, override_get_current_user, override_get_db):
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

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
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
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = response.json()
    assert body["detail"] == "期限が過去の日付になっています"
