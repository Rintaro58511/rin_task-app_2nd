from unittest.mock import AsyncMock
import pytest
from routers import tasks
from httpx import ASGITransport, AsyncClient
from main import app
from datetime import datetime, date
from models.tasks import Task
from enums import TaskStatus


@pytest.mark.anyio
async def test_search_task(
    monkeypatch,
    other_task,
    override_get_current_other_task_user,
    override_get_db,
):
    async def mock_fetch_task(task_id, user_id, db):
        return other_task

    monkeypatch.setattr(tasks, "fetch_task", mock_fetch_task)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/tasks/{other_task.task_id}"
        )

    assert response.status_code == 200
    body = response.json()

    assert body["task_name"] == other_task.task_name

@pytest.mark.anyio
async def test_fail_fetch_task(
    monkeypatch,
    task,
    override_get_current_task_user,
    override_get_db,
):
    async def mock_fail_fetch_task(task_id, user_id, db):
        return None

    monkeypatch.setattr(
        tasks,
        "fetch_task",
        mock_fail_fetch_task
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/tasks/{task.task_id}"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "指定されたタスクが見つかりません"

@pytest.mark.anyio
async def test_fetch_other_user_task(
    monkeypatch,
    task,
    other_task,
    override_get_current_other_task_user,
    override_get_db,
):
    async def mock_fetch_another_user_task(task_id, user_id, db):
        return task

    monkeypatch.setattr(
        tasks,
        "fetch_task",
        mock_fetch_another_user_task
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/tasks/{task.task_id}"
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "他ユーザーのタスクです"