from fastapi import APIRouter, status, HTTPException
from schemas.tasks import UpdateAndCreateTaskSchema, TaskSchema, ResponseSchema
from cruds.tasks import add_task, fetch_tasks, remove_task, modify_task

router = APIRouter()


@router.post(
    "/tasks", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_task(task: UpdateAndCreateTaskSchema):
    new_task = await add_task(task)
    return ResponseSchema(message="タスク追加ができました", task=new_task)


@router.get("/tasks", response_model=list[TaskSchema])
async def list_task():
    tasks = await fetch_tasks()
    return tasks


@router.delete("/tasks/{task_id}", response_model=ResponseSchema)
async def delete_task(task_id: int):
    deleted_task = await remove_task(task_id)
    return ResponseSchema(message="タスクを削除しました", task=deleted_task)


@router.put("/tasks/{task_id}", response_model=ResponseSchema)
async def update_task(task_id: int, task: UpdateAndCreateTaskSchema):
    updated_task = await modify_task(task_id, task)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="指定されたタスクが存在しません")
    return ResponseSchema(message="タスクを更新しました", task=updated_task)
