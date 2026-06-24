from schemas.tasks import TaskSchema, UpdateAndCreateTaskSchema

task_db = []

async def list_task():
    return task_db

async def add_task(task: UpdateAndCreateTaskSchema):
    max_task_id = max([t.task_id for t in task_db]) + 1 if task_db else 1
    new_task = TaskSchema(task_id=max_task_id,
                      task_name=task.task_name,
                      task_deadline=task.task_deadline,
                      task_detail=task.task_detail)
    task_db.append(new_task)
    return new_task