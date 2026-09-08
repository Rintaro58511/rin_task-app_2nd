from datetime import datetime, timezone

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_fetch_subtask_list(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/tasks/{test_task.task_id}/subtasks")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data[0]["subtask_id"] == str(test_subtask.subtask_id)
    assert data[0]["subtask_name"] == test_subtask.subtask_name
    assert datetime.fromisoformat(data[0]["created_at"]) == datetime(2026, 8, 15, tzinfo=timezone.utc)
