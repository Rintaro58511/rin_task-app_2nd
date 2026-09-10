import uuid
from datetime import datetime, timezone

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from enums import TaskStatus
from main import app


@pytest.mark.asyncio
async def test_get_task(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/tasks/{test_task.task_id}")
    assert response.status_code == status.HTTP_200_OK

    expected_etag = f'"{int(test_task.changed_time.timestamp())}"'
    assert response.headers["Etag"] == expected_etag

    data = response.json()
    assert data["task_id"] == str(test_task.task_id)
    assert data["task_name"] == "test_task"
    assert datetime.fromisoformat(data["changed_time"]) == datetime(2026, 8, 16, tzinfo=timezone.utc)
    assert data["task_status"]["task_progress"] == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_get_task_with_etag(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        first_response = await ac.get(f"/tasks/{test_task.task_id}")

        etag = first_response.headers["ETag"]

        second_response = await ac.get(
            f"/tasks/{test_task.task_id}", headers={"If-None-Match": etag},
        )

    assert first_response.status_code == status.HTTP_200_OK
    assert second_response.status_code == status.HTTP_304_NOT_MODIFIED


@pytest.mark.asyncio
async def test_get_task_with_old_etag(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        old_etag = f'"{int(test_task.changed_time.timestamp()) - 1}"'
        response = await ac.get(f"/tasks/{test_task.task_id}", headers={"If-None-Match": old_etag})

    expected_etag = f'"{int(test_task.changed_time.timestamp())}"'
    assert response.headers["Etag"] == expected_etag
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_none_task(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    none_task_id = uuid.uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/tasks/{none_task_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "指定されたタスクが見つかりません"
