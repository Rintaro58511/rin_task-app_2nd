import uuid

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from main import app
from routers import tasks


@pytest.mark.anyio
async def test_update_task(
    monkeypatch,
    other_task,
    override_get_current_user,
    override_get_mock_db,
):

    async def mock_fetch_task(task_id, user_id, db):
        return other_task

    monkeypatch.setattr(tasks, "fetch_task", mock_fetch_task)

    payload = {
        "task_name": "test_task_update",
        "task_deadline": "2027-08-01",
        "task_detail": "コードのリファクタリング",
        "task_status": {
            "task_progress": "IN_PROGRESS",
            "progress_ratio": 90,
            "progress_comment": "終わりそう",
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/tasks/{other_task.task_id}", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "タスクを更新しました"


@pytest.mark.anyio
async def test_update_none_task(
    monkeypatch,
    other_task,
    override_get_current_user,
    override_get_mock_db,
):

    async def mock_fetch_task(task_id, user_id, db):
        return None

    monkeypatch.setattr(tasks, "fetch_task", mock_fetch_task)

    payload = {
        "task_name": "test_task_update",
        "task_deadline": "2026-08-01",
        "task_detail": "コードのリファクタリング",
        "changed_time": "2026-07-30T11:11:11",
        "task_status": {
            "task_progress": "IN_PROGRESS",
            "progress_ratio": 90,
            "progress_comment": "終わりそう",
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/tasks/{other_task.task_id}", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "指定されたタスクが存在しません"


@pytest.mark.anyio
async def test_update_other_user(
    monkeypatch,
    other_task,
    override_get_current_user,
    override_get_mock_db,
):

    other_task.user_id = uuid.uuid4()

    async def mock_fetch_task(task_id, user_id, db):
        return other_task

    monkeypatch.setattr(tasks, "fetch_task", mock_fetch_task)

    payload = {
        "task_name": "test_task_update",
        "task_deadline": "2026-08-01",
        "task_detail": "コードのリファクタリング",
        "task_status": {
            "task_progress": "IN_PROGRESS",
            "progress_ratio": 90,
            "progress_comment": "終わりそう",
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/tasks/{other_task.task_id}", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "指定されたタスクが存在しません"


@pytest.mark.anyio
async def test_update_expired_task(
    monkeypatch,
    other_task,
    override_get_current_user,
    override_get_mock_db,
):

    async def mock_fetch_task(task_id, user_id, db):
        return other_task

    monkeypatch.setattr(tasks, "fetch_task", mock_fetch_task)

    payload = {
        "task_name": "test_task_update",
        "task_deadline": "2026-08-01",
        "task_detail": "コードのリファクタリング",
        "task_status": {
            "task_progress": "IN_PROGRESS",
            "progress_ratio": 90,
            "progress_comment": "終わりそう",
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/tasks/{other_task.task_id}", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "期限が過去の日付になっています"


@pytest.mark.anyio
async def test_updated_task(
    monkeypatch,
    other_task,
    override_get_current_user,
    override_get_mock_db,
):

    async def mock_fetch_task(task_id, user_id, db):
        return other_task

    monkeypatch.setattr(tasks, "fetch_task", mock_fetch_task)

    payload = {
        "task_name": "test_task_update",
        "task_deadline": "2027-08-01",
        "task_detail": "コードのリファクタリング",
        "task_status": {
            "task_progress": "IN_PROGRESS",
            "progress_ratio": 90,
            "progress_comment": "終わりそう",
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(
            f"/tasks/{other_task.task_id}",
            headers={"If-Match": '"invalid-etag"'},
            json=payload,
        )

    assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert response.json() == {
        "detail": "タスクが他のユーザーによって更新されています。最新データを再取得してください"
    }
