import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app
from routers import subtasks


@pytest.mark.anyio
async def test_search_subtask(
    monkeypatch,
    subtask,
    override_get_db,
    override_get_current_user
    ):

    async def mock_fetch_subtask(subtask_id, user_id, db):
        return subtask
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/tasks/subtasks/{subtask.subtask_id}"
        )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["subtask_id"] == str(subtask.subtask_id)
    assert body["subtask_name"] == "test_subtask"
    assert body["is_complete"] is False
    assert body["created_at"] == subtask.created_at.isoformat()

@pytest.mark.anyio
async def test_search_none_subtask(
    monkeypatch,
    subtask,
    override_get_db,
    override_get_current_user
    ):

    async def mock_fetch_none_subtask(subtask_id, user_id, db):
        return None
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_none_subtask)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/tasks/subtasks/{subtask.subtask_id}"
        )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body["detail"] == "指定されたサブタスクが見つかりません"
