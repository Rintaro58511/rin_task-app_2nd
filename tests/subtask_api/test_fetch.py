import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock

from main import app

from routers import subtasks

import db

@pytest.fixture
def override_get_db():

    async def override_db():
        yield AsyncMock()

    app.dependency_overrides[db.get_db_session] = override_db

    yield

    app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_search_subtask(monkeypatch, subtask, override_get_db):

    async def mock_fetch_subtask(subtask_id, db):
        return subtask
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_subtask)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/tasks/subtasks/{subtask.subtask_id}"
        )
    assert response.status_code == 200
    body = response.json()
    assert body["subtask_id"] == str(subtask.subtask_id)
    assert body["subtask_name"] == "test_subtask"
    assert body["is_complete"] == False
    assert body["created_at"] == subtask.created_at.isoformat()

@pytest.mark.anyio
async def test_search_none_subtask(monkeypatch, subtask, override_get_db):

    async def mock_fetch_none_subtask(subtask_id, db):
        return None
    monkeypatch.setattr(subtasks, "fetch_subtask", mock_fetch_none_subtask)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            f"/tasks/subtasks/{subtask.subtask_id}"
        )
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "指定されたサブタスクが見つかりません"
