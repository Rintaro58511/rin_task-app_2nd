from fastapi import (
    APIRouter,
    status,
    HTTPException,
    Depends,
    Response,
    Header
)
from cruds.tasks import(
    fetch_task
)
from schemas.subtasks import (
    UpdateAndCreateSubTaskSchema,
    SubTaskSchema,
    ResponseSchema
)
from service.subtasks import(
    calculate_ratio
)
from cruds.subtasks import (
    add_subtask,
    fetch_subtasks,
    remove_subtask,
    modify_subtask,
    fetch_subtask,
)
from sqlalchemy.ext.asyncio import AsyncSession
import db
from uuid import UUID
from datetime import date

router = APIRouter()

@router.post(
    "/tasks/subtasks", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_subtask(
    subtask: UpdateAndCreateSubTaskSchema,
    task_id: UUID,
    db_session: AsyncSession = Depends(db.get_db_session),
) -> ResponseSchema:
    """サブタスクの追加を行い、エラーの場合はメッセージを返す"""

    task = await fetch_task(task_id, db_session)
    if task is None:
        raise HTTPException(status_code=404, detail="タスクが存在しません")
    await add_subtask(subtask, task_id, db_session)
    await db_session.flush()
    progress_ratio = await calculate_ratio(task_id, db_session)
    task.progress_ratio = progress_ratio
    await db_session.commit()
    return ResponseSchema(status_code=201, detail="サブタスクを登録しました")
