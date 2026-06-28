from schemas.tasks import TaskSchema, UpdateAndCreateTaskSchema
from models.tasks import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

async def fetch_task(task_id: uuid.UUID,
                     db_session: AsyncSession) -> Task:
    result = await db_session.execute(select(Task).filter(Task.task_id == task_id))
    target_task = result.scalars().first()

    return target_task

async def fetch_tasks(db_session: AsyncSession) -> list[Task]:
    results = await db_session.execute(select(Task))
    target_tasks = results.scalars().all()

    return target_tasks

async def add_task(task: UpdateAndCreateTaskSchema,
                   db_session: AsyncSession) -> Task:
    new_task = Task(**task.model_dump())
    db_session.add(new_task)
    await db_session.commit()
    await db_session.refresh(new_task)

    return new_task

async def remove_task(task_id: uuid.UUID,
                      db_session: AsyncSession) -> None:
    target_task = await fetch_task(task_id, db_session)
    if target_task:
        db_session.delete(target_task)
        await db_session.commit()

async def modify_task(task: UpdateAndCreateTaskSchema,
                      task_id: uuid.UUID,
                      db_session: AsyncSession) -> Task:
    target_task = await fetch_task(task_id, db_session)
    if target_task:
        target_task.task_name = task.task_name
        target_task.task_deadline = task.task_deadline
        target_task.task_detail = task.task_detail
    await db_session.commit()
    await db_session.refresh(target_task)

    return target_task
