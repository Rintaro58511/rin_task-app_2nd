from schemas.tasks import TaskSchema, UpdateAndCreateTaskSchema

task_db = []

async def fetch_tasks():
    return task_db

async def add_task(task: UpdateAndCreateTaskSchema):
    max_task_id = max([t.task_id for t in task_db]) + 1 if task_db else 1
    new_task = TaskSchema(task_id=max_task_id,
                      task_name=task.task_name,
                      task_deadline=task.task_deadline,
                      task_detail=task.task_detail)
    task_db.append(new_task)
    return new_task

async def remove_task(task_id: int):
    deleted_task = task_db.pop(task_id-1)
    return deleted_task