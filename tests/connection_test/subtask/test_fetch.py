from datetime import datetime, timezone

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_search_subtask(
    connection_test,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/tasks/subtasks/{test_subtask.subtask_id}")
    assert response.status_code == status.HTTP_200_OK
    assert test_task.task_name == "test_task"
    assert test_task.progress_ratio == 80
    assert test_subtask.subtask_name == "test_subtask"
    assert test_subtask.created_at == datetime(2026, 8, 15, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_search_other_user_subtask(
    connection_test,
    override_get_test_db,
    override_get_test_other_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/tasks/subtasks/{test_subtask.subtask_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
