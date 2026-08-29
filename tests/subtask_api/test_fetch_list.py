import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app
from routers import subtasks


@pytest.mark.anyio
async def test_get_subtasks(monkeypatch, subtask_list, override_get_db, override_get_current_user):

    async def mock_fetch_subtasks(task_id, user_id, db):
        return subtask_list

    monkeypatch.setattr(subtasks, "fetch_subtasks", mock_fetch_subtasks)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/tasks/{subtask_list[0].task_id}/subtasks")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body[0]["subtask_id"] == str(subtask_list[0].subtask_id)
    assert body[0]["subtask_name"] == "test_subtask1"
    assert body[0]["is_complete"] is True
    assert body[0]["created_at"] == subtask_list[0].created_at.isoformat()
    assert body[1]["subtask_id"] == str(subtask_list[1].subtask_id)
    assert body[1]["subtask_name"] == "test_subtask2"
    assert body[1]["is_complete"] is False
    assert body[1]["created_at"] == subtask_list[1].created_at.isoformat()
