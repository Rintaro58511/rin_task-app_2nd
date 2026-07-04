from fastapi import APIRouter, status, HTTPException, Depends
from schemas.tasks import UpdateAndCreateTaskSchema, TaskSchema, ResponseSchema
from cruds.tasks import (
    add_task,
    fetch_tasks,
    remove_task,
    modify_task,
    fetch_task,
    sort_tasks,
)
from sqlalchemy.ext.asyncio import AsyncSession
import db
from uuid import UUID
from routers.user import get_current_user

router = APIRouter()


@router.post(
    "/tasks", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_task(
    task: UpdateAndCreateTaskSchema,
    db_session: AsyncSession = Depends(db.get_db_session),
    current_user=Depends(get_current_user),
):

    try:
        new_task = await add_task(task, db_session, current_user.user_id)
        dict_task = TaskSchema(
            task_id=new_task.task_id,
            task_name=new_task.task_name,
            task_deadline=new_task.task_deadline,
            task_detail=new_task.task_detail,
            task_status=new_task.task_status,
        )
        return ResponseSchema(message="タスク追加ができました", task=dict_task)
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=400, detail="タスクの登録に失敗しました。")


@router.get("/tasks", response_model=list[TaskSchema])
async def list_task(
    db_session: AsyncSession = Depends(db.get_db_session),
    current_user=Depends(get_current_user),
):
    tasks = await fetch_tasks(db_session, current_user.user_id)
    return tasks


@router.delete("/tasks/{task_id}", response_model=ResponseSchema)
async def delete_task(
    task_id: UUID,
    db_session: AsyncSession = Depends(db.get_db_session),
    current_user=Depends(get_current_user),
):
    deleted_task = await fetch_task(task_id, db_session)
    if deleted_task is None:
        raise HTTPException(status_code=400, detail="タスクの削除に失敗しました。")
    if deleted_task.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="他ユーザーのタスクです。")
    dict_task = TaskSchema(
        task_id=deleted_task.task_id,
        task_name=deleted_task.task_name,
        task_deadline=deleted_task.task_deadline,
        task_detail=deleted_task.task_detail,
        task_status=deleted_task.task_status,
    )
    await remove_task(task_id, db_session)
    return ResponseSchema(message="タスクを削除しました", task=dict_task)


@router.put("/tasks/{task_id}", response_model=ResponseSchema)
async def update_task(
    task_id: UUID,
    task: UpdateAndCreateTaskSchema,
    db_session: AsyncSession = Depends(db.get_db_session),
    current_user=Depends(get_current_user),
):
    target_task = await fetch_task(task_id, db_session)
    if target_task is None:
        raise HTTPException(status_code=400, detail="指定されたタスクが存在しません。")
    if target_task.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="他ユーザーのタスクです。")
    updated_task = await modify_task(task, target_task, db_session)
    dict_task = TaskSchema(
        task_id=updated_task.task_id,
        task_name=updated_task.task_name,
        task_deadline=updated_task.task_deadline,
        task_detail=updated_task.task_detail,
        task_status=updated_task.task_status,
    )
    return ResponseSchema(message="タスクを更新しました", task=dict_task)


@router.get("/tasks/{task_id}", response_model=TaskSchema)
async def search_task(
    task_id: UUID, db_session: AsyncSession = Depends(db.get_db_session)
):
    task = await fetch_task(task_id, db_session)
    return task


@router.get("/tasks", response_model=list[TaskSchema])
async def sort_tasks(
    sort: str = "asc",
    db_session: AsyncSession = Depends(db.get_db_session),
    current_user=Depends(get_current_user),
):
    sorted_tasks = await sort_tasks(db_session, current_user.user_id, sort)
    return sorted_tasks
