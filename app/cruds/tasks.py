from schemas.tasks import TaskSchema, UpdateAndCreateTaskSchema

task_db = []

async def fetch_tasks():
    return task_db

async def add_task(task: UpdateAndCreateTaskSchema):
    max_task_id = max([t.task_id for t in task_db]) + 1 if task_db else 1
    new_task = TaskSchema(task_id=max_task_id, **task.model_dump())
    task_db.append(new_task)
    return new_task

async def remove_task(task_id: int):
    deleted_task = task_db.pop(task_id-1)
    return deleted_task

async def modify_task(task_id: int, task: TaskSchema):

    for index, existing_task in enumerate(task_db):

        if existing_task.task_id == task_id:
            updated_task = TaskSchema(task_id = task_id, **task.model_dump())
            task_db[index] = updated_task
            return updated_task
    
    return None

async def fetch_task(task_id: int):
    for index, existing_task in enumerate(task_db):

        if existing_task.task_id == task_id:
            return task_db[index]
        
    return None
