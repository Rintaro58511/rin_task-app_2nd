from schemas.tasks import TaskSchema, UpdateAndCreateTaskSchema
from models.tasks import Task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID


async def fetch_task(task_id: UUID, db_session: AsyncSession) -> Task:
    result = await db_session.execute(select(Task).filter(Task.task_id == task_id))
    target_task = result.scalars().first()

    return target_task


async def fetch_tasks(db_session: AsyncSession, user_id: UUID) -> list[Task]:
    results = await db_session.execute(select(Task).where(Task.user_id == user_id))
    target_tasks = results.scalars().all()

    return target_tasks


async def add_task(
    task: UpdateAndCreateTaskSchema, db_session: AsyncSession, user_id: UUID
) -> Task:
    new_task = Task(**task.model_dump(), user_id=user_id)
    db_session.add(new_task)
    await db_session.commit()
    await db_session.refresh(new_task)

    return new_task


async def remove_task(task_id: UUID, db_session: AsyncSession) -> None:
    target_task = await fetch_task(task_id, db_session)
    if target_task:
        db_session.delete(target_task)
        await db_session.commit()


async def modify_task(
    task: UpdateAndCreateTaskSchema, target_task: Task, db_session: AsyncSession
) -> Task:
    target_task.task_name = task.task_name
    target_task.task_deadline = task.task_deadline
    target_task.task_detail = task.task_detail
    target_task.task_status = task.task_status
    await db_session.commit()
    await db_session.refresh(target_task)

    return target_task


async def sort_tasks(
    db_session: AsyncSession, user_id: UUID, sort_order: str = "asc"
) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id)

    if sort_order == "desc":
        stmt = stmt.order_by(Task.task_deadline.desc())
    else:
        stmt = stmt.order_by(Task.task_deadline.asc())

    result = await db_session.execute(stmt)
    return list(result.scalars().all())
