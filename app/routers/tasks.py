from fastapi import APIRouter, status, HTTPException, Depends
from schemas.tasks import UpdateAndCreateTaskSchema, TaskSchema, ResponseSchema
from cruds.tasks import add_task, fetch_tasks, remove_task, modify_task, fetch_task
from sqlalchemy.ext.asyncio import AsyncSession
import db
from uuid import UUID

router = APIRouter()

@router.post("/tasks", response_model = ResponseSchema, status_code = status.HTTP_201_CREATED)
async def create_task(task: UpdateAndCreateTaskSchema,
                      db_session: AsyncSession = Depends(db.get_db_session)):
    # new_task = await add_task(task, db_session)
    # dict_task = TaskSchema(
    #     task_id = new_task.task_id,
    #     task_name = new_task.task_name,
    #     task_deadline = new_task.task_deadline,
    #     task_detail = new_task.task_detail
    # )
    # return ResponseSchema(message = "タスク追加ができました", task=dict_task)
    try:
        new_task = await add_task(task, db_session)
        dict_task = TaskSchema(
        task_id = new_task.task_id,
        task_name = new_task.task_name,
        task_deadline = new_task.task_deadline,
        task_detail = new_task.task_detail
        )
        return ResponseSchema(message = "タスク追加ができました", task=dict_task)
    except Exception as e:
        raise HTTPException(status_code=400, detail="タスクの登録に失敗しました。")

@router.get("/tasks", response_model = list[TaskSchema])
async def list_task(db_session: AsyncSession = Depends(db.get_db_session)):
    tasks = await fetch_tasks(db_session)
    return tasks

@router.delete("/tasks/{task_id}", response_model = ResponseSchema)
async def delete_task(task_id: UUID, db_session: AsyncSession = Depends(db.get_db_session)):
    deleted_task = await fetch_task(task_id, db_session)
    if deleted_task is None:
        raise HTTPException(status_code=400, detail="タスクの削除に失敗しました。")
    dict_task = TaskSchema(
        task_id = deleted_task.task_id,
        task_name = deleted_task.task_name,
        task_deadline = deleted_task.task_deadline,
        task_detail = deleted_task.task_detail
        )
    await remove_task(task_id, db_session)
    return ResponseSchema(message="タスクを削除しました", task = dict_task)

@router.put("/tasks/{task_id}", response_model = ResponseSchema)
async def update_task(task_id: UUID,
                      task: UpdateAndCreateTaskSchema,
                      db_session: AsyncSession = Depends(db.get_db_session)):
    updated_task = await modify_task(task, task_id, db_session)
    if updated_task is None:
        raise HTTPException(status_code = 404, detail = "指定されたタスクが存在しません")
    dict_task = TaskSchema(
        task_id = task_id,
        task_name = updated_task.task_name,
        task_deadline = updated_task.task_deadline,
        task_detail = updated_task.task_detail
    )
    return ResponseSchema(message="タスクを更新しました", task = dict_task)

@router.get("/tasks/{task_id}", response_model = TaskSchema)
async def search_task(task_id: UUID, db_session: AsyncSession = Depends(db.get_db_session)):
    task = await fetch_task(task_id, db_session)
    return task
