from fastapi import APIRouter
from schemas.tasks import UpdateAndCreateTaskSchema, TaskSchema, ResponseSchema
from cruds.tasks import add_task, fetch_tasks

router = APIRouter()

@router.post("/tasks", response_model = ResponseSchema)
async def create_task(task: UpdateAndCreateTaskSchema):
    new_task = await add_task(task)
    return ResponseSchema(message = "タスク追加ができました", task=new_task)

@router.get("/tasks", response_model = list[TaskSchema])
async def list_task():
    tasks = await fetch_tasks()
    return tasks