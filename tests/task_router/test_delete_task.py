import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app
from routers import tasks


@pytest.mark.anyio
async def test_delete_task(monkeypatch, task, override_get_current_task_user, override_get_db):

    async def mock_fetch_task(task_id, user_id, db):
        return task

    monkeypatch.setattr(tasks, "fetch_task", mock_fetch_task)

    async def mock_remove_task(task_id, db):
        return None

    monkeypatch.setattr(tasks, "remove_task", mock_remove_task)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete(
            f"/tasks/{task.task_id}",
        )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["message"] == "タスクを削除しました"
