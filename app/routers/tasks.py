from fastapi import APIRouter
from schemas.tasks import UpdateAndCreateTaskSchema, TaskSchema, ResponseSchema

router = APIRouter()

@router.post("/tasks", response_model = ResponseSchema)
async def create_task(task: UpdateAndCreateTaskSchema):
    #ここにタスク追加操作
    dummy_task = TaskSchema(
        task_id=1,
        task_name=task.task_name,
        task_deadline=task.task_deadline,
        task_detail=task.task_detail
    )
    return ResponseSchema(message = "タスク追加ができました", task=dummy_task)