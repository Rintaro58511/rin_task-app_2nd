from datetime import datetime, timezone
from uuid import UUID

import db
from cruds.subtasks import (
    add_subtask,
    fetch_subtask,
    fetch_subtasks,
    modify_subtask,
    remove_subtask,
)
from cruds.tasks import fetch_task
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from schemas.subtasks import ResponseSchema, SubTaskSchema, UpdateAndCreateSubTaskSchema
from service.subtasks import (
    calculate_ratio,
    check_progress,
)
from sqlalchemy.ext.asyncio import AsyncSession

from routers.user import get_current_user

router = APIRouter()


@router.post(
    "/tasks/{task_id}/subtask", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_subtask(
    subtask: UpdateAndCreateSubTaskSchema,
    task_id: UUID,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
) -> ResponseSchema:
    """サブタスクの追加を行い、エラーの場合はメッセージを返す"""

    task = await fetch_task(task_id, current_user.user_id, db_session)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="タスクが存在しません")

    await add_subtask(subtask, task_id, db_session)
    await db_session.flush()

    progress_ratio = await calculate_ratio(task_id, current_user.user_id, db_session)
    task.progress_ratio = progress_ratio

    task_progress = await check_progress(progress_ratio, db_session)
    task.task_progress = task_progress

    task.changed_time = datetime.now(timezone.utc)

    await db_session.commit()
    return ResponseSchema(status_code=status.HTTP_201_CREATED, message="サブタスクを登録しました")


@router.get("/tasks/subtasks/{subtask_id}", response_model=SubTaskSchema)
async def search_subtask(
    subtask_id: UUID,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
):
    """指定されたIDのサブタスクを取得する"""

    subtask = await fetch_subtask(subtask_id, current_user.user_id, db_session)
    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="指定されたサブタスクが見つかりません"
        )

    return subtask


@router.get("/tasks/{task_id}/subtasks", response_model=list[SubTaskSchema])
async def get_subtasks(
    task_id: UUID,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
):
    """指定されたタスクIDのサブタスクを取得する"""

    subtask_list = await fetch_subtasks(task_id, current_user.user_id, db_session)

    return subtask_list


@router.put("/tasks/{task_id}/subtasks/{subtask_id}", response_model=ResponseSchema)
async def update_subtask(
    subtask_schema: UpdateAndCreateSubTaskSchema,
    subtask_id: UUID,
    task_id: UUID,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
):
    """指定されたサブタスクIDのサブタスクを更新する"""

    task = await fetch_task(task_id, current_user.user_id, db_session)
    if task is None:
        raise HTTPException(status_code=404, detail="指定されたタスクが存在しません")

    target_subtask = await fetch_subtask(subtask_id, current_user.user_id, db_session)

    if target_subtask is None:
        raise HTTPException(status_code=404, detail="指定されたサブタスクが存在しません")

    if task_id != target_subtask.task_id:
        raise HTTPException(status_code=400, detail="親タスクが異なります")

    await modify_subtask(subtask_schema, target_subtask)
    await db_session.flush()

    progress_ratio = await calculate_ratio(task_id, current_user.user_id, db_session)
    task.progress_ratio = progress_ratio

    task_progress = await check_progress(progress_ratio, db_session)
    task.task_progress = task_progress

    task.changed_time = datetime.now(timezone.utc)

    await db_session.commit()

    return ResponseSchema(message="サブタスクを更新しました")


@router.delete("/tasks/{task_id}/subtasks/{subtask_id}", response_model=ResponseSchema)
async def delete_subtask(
    subtask_id: UUID,
    task_id: UUID,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
):
    """指定されたサブタスクIDのサブタスクを削除する"""

    task = await fetch_task(task_id, current_user.user_id, db_session)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="指定されたタスクが存在しません"
        )

    target_subtask = await fetch_subtask(subtask_id, current_user.user_id, db_session)
    if target_subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="指定されたサブタスクが存在しません"
        )
    if task_id != target_subtask.task_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="親タスクが異なります")

    await remove_subtask(target_subtask, db_session)
    await db_session.flush()

    progress_ratio = await calculate_ratio(task_id, current_user.user_id, db_session)
    if progress_ratio is not None:
        task.progress_ratio = progress_ratio

        task_progress = await check_progress(progress_ratio, db_session)
        task.task_progress = task_progress

    task.changed_time = datetime.now(timezone.utc)

    await db_session.commit()

    return ResponseSchema(message="サブタスクを削除しました")
