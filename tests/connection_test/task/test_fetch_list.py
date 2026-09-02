import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.mark.asyncio
async def test_fetch_task_list(
    connection_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/tasks")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data[0]["task_name"] == test_task.task_name
    assert data[1]["task_name"] == other_task.task_name
    assert data[0]["task_status"]["progress_ratio"] == test_task.progress_ratio
    assert data[1]["task_status"]["progress_ratio"] == other_task.progress_ratio


@pytest.mark.asyncio
async def test_arrange_task_deadline(
    connection_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/tasks",
            params={"sort": "deadline"},
        )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data[0]["task_name"] == other_task.task_name
    assert data[1]["task_name"] == test_task.task_name
    assert data[0]["task_status"]["progress_ratio"] == other_task.progress_ratio
    assert data[1]["task_status"]["progress_ratio"] == test_task.progress_ratio


@pytest.mark.asyncio
async def test_arrange_task_status(
    connection_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = connection_test

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/tasks",
            params={"sort": "status"},
        )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data[0]["task_name"] == other_task.task_name
    assert data[1]["task_name"] == test_task.task_name
    assert data[0]["task_status"]["progress_ratio"] == other_task.progress_ratio
    assert data[1]["task_status"]["progress_ratio"] == test_task.progress_ratio
