from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

import db
from cruds.tasks import (
    add_task,
    arrange_tasks,
    fetch_task,
    fetch_tasks,
    filter_tasks,
    modify_task,
    remove_task,
)
from routers.user import get_current_user
from schemas.tasks import (
    ResponseSchema,
    TaskSchema,
    TaskStatusSchema,
    UpdateAndCreateTaskSchema,
)

router = APIRouter()


@router.post("/tasks", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: UpdateAndCreateTaskSchema,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
) -> ResponseSchema:
    """タスクの追加を行い、結果メッセージを返す"""

    if task.task_deadline < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="期限が過去の日付になっています"
        )

    await add_task(task, current_user.user_id, db_session)
    return ResponseSchema(message="タスク追加ができました")


@router.get("/tasks/{task_id}", response_model=TaskSchema)
async def search_task(
    task_id: UUID,
    response: Response,
    if_none_match: str | None = Header(None),
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
) -> TaskSchema:
    """指定されたIDのタスク詳細を取得する"""

    task = await fetch_task(task_id, current_user.user_id, db_session)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="指定されたタスクが見つかりません"
        )
    if task.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他ユーザーのタスクです")

    etag = f'"{int(task.changed_time.timestamp())}"'

    if if_none_match == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    response.headers["ETag"] = etag

    task_status = TaskStatusSchema(
        task_progress=task.task_progress,
        progress_ratio=task.progress_ratio,
        progress_comment=task.progress_comment,
    )
    task_pydantic = TaskSchema(
        task_id=task.task_id,
        task_name=task.task_name,
        task_deadline=task.task_deadline,
        task_detail=task.task_detail,
        task_status=task_status,
    )

    return task_pydantic


@router.get("/tasks", response_model=list[TaskSchema])
async def get_tasks(
    sort: str | None = None,
    search_name: str | None = None,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
) -> list[TaskSchema]:
    """ソートや絞り込み条件に応じて、ログインユーザーのタスク一覧を取得する"""

    if sort in ["deadline", "status"]:
        tasks = await arrange_tasks(sort, current_user.user_id, db_session)
    elif search_name:
        tasks = await filter_tasks(search_name, current_user.user_id, db_session)
    else:
        tasks = await fetch_tasks(current_user.user_id, db_session)

    tasks_pydantic = []

    for task in tasks:
        task_status = TaskStatusSchema(
            task_progress=task.task_progress,
            progress_ratio=task.progress_ratio,
            progress_comment=task.progress_comment,
        )
        task_pydantic = TaskSchema(
            task_id=task.task_id,
            task_name=task.task_name,
            task_deadline=task.task_deadline,
            task_detail=task.task_detail,
            task_status=task_status,
        )
        tasks_pydantic.append(task_pydantic)

    return tasks_pydantic


@router.put("/tasks/{task_id}", response_model=ResponseSchema)
async def update_task(
    task_id: UUID,
    task: UpdateAndCreateTaskSchema,
    if_match: str | None = Header(None),
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
) -> ResponseSchema:
    """指定されたIDのタスク情報を更新する"""

    target_task = await fetch_task(task_id, current_user.user_id, db_session)

    if task.task_deadline < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="期限が過去の日付になっています"
        )
    if target_task is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="指定されたタスクが存在しません"
        )
    if target_task.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他ユーザーのタスクです")

    current_etag = f'"{int(target_task.changed_time.timestamp())}"'

    if if_match and if_match != current_etag:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="タスクが他のユーザーによって更新されています。最新データを再取得してください",
        )

    await modify_task(task, target_task, db_session)

    return ResponseSchema(message="タスクを更新しました")


@router.delete("/tasks/{task_id}", response_model=ResponseSchema)
async def delete_task(
    task_id: UUID,
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
) -> ResponseSchema:
    """指定されたIDのタスクを削除する"""

    deleted_task = await fetch_task(task_id, current_user.user_id, db_session)

    if deleted_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="指定されたタスクが見つかりません"
        )

    return ResponseSchema(message="タスクを削除しました")
