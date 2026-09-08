import uuid

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from enums import TaskStatus
from main import app
from models.tasks import Task


@pytest.mark.asyncio
async def test_update_task(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    payload = {
        "task_name": "integration_test_task",
        "task_deadline": "2026-09-30",
        "task_detail": None,
        "task_status": {
            "task_progress": TaskStatus.DONE,
            "progress_ratio": 100,
            "progress_comment": "終了",
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/tasks/{test_task.task_id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "タスクを更新しました"

    result = await db_session.execute(select(Task).where(Task.task_id == test_task.task_id))
    await db_session.refresh(test_task)
    updated_task = result.scalar_one_or_none()

    assert updated_task is not None
    assert updated_task.task_name == "integration_test_task"


@pytest.mark.asyncio
async def test_update_past_task(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    payload = {
        "task_name": "integration_test_task",
        "task_deadline": "2026-08-30",
        "task_detail": None,
        "task_status": {
            "task_progress": TaskStatus.TODO,
            "progress_ratio": 0,
            "progress_comment": None,
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/tasks/{test_task.task_id}", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "期限が過去の日付になっています"

    result = await db_session.execute(select(Task).where(Task.task_id == test_task.task_id))
    await db_session.refresh(test_task)
    updated_task = result.scalar_one_or_none()

    assert updated_task is not None
    assert updated_task.task_name == "test_task"


@pytest.mark.asyncio
async def test_fetch_none_task(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    payload = {
        "task_name": "integration_test_task",
        "task_deadline": "2026-10-30",
        "task_detail": None,
        "task_status": {
            "task_progress": TaskStatus.TODO,
            "progress_ratio": 0,
            "progress_comment": None,
        },
    }
    none_task_id = uuid.uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/tasks/{none_task_id}", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "指定されたタスクが存在しません"

    result = await db_session.execute(select(Task).where(Task.task_id == test_task.task_id))
    await db_session.refresh(test_task)
    updated_task = result.scalar_one_or_none()

    assert updated_task is not None
    assert updated_task.task_name == "test_task"


@pytest.mark.asyncio
async def test_fetch_other_user_task(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_other_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    payload = {
        "task_name": "integration_test_task",
        "task_deadline": "2026-10-30",
        "task_detail": None,
        "task_status": {
            "task_progress": TaskStatus.TODO,
            "progress_ratio": 0,
            "progress_comment": None,
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.put(f"/tasks/{test_task.task_id}", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "指定されたタスクが存在しません"

    result = await db_session.execute(select(Task).where(Task.task_id == test_task.task_id))
    await db_session.refresh(test_task)
    updated_task = result.scalar_one_or_none()

    assert updated_task is not None
    assert updated_task.task_name == "test_task"


@pytest.mark.asyncio
async def test_update_task_with_etag(
    integration_test,
    db_session,
    override_get_test_db,
    override_get_test_current_user,
):
    test_user, test_other_user, test_task, test_subtask, other_task = integration_test

    payload = {
        "task_name": "integration_test_task",
        "task_deadline": "2026-10-30",
        "task_detail": None,
        "task_status": {
            "task_progress": TaskStatus.TODO,
            "progress_ratio": 0,
            "progress_comment": None,
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        old_etag = f'"{int(test_task.changed_time.timestamp()) - 1}"'
        response = await ac.put(
            f"/tasks/{test_task.task_id}", headers={"If-Match": old_etag}, json=payload
        )

    assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
    assert (
        response.json()["detail"]
        == "タスクが他のユーザーによって更新されています。最新データを再取得してください"
    )

    result = await db_session.execute(select(Task).where(Task.task_id == test_task.task_id))
    await db_session.refresh(test_task)
    updated_task = result.scalar_one_or_none()

    assert updated_task is not None
    assert updated_task.task_name == "test_task"
