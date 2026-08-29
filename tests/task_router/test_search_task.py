import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app
from routers import tasks


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

    assert response.status_code == status.HTTP_200_OK
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

    assert response.status_code == status.HTTP_404_NOT_FOUND
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

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "他ユーザーのタスクです"