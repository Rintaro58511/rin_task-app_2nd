from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from cruds.subtasks import fetch_subtasks
from enums import TaskStatus


async def check_progress(progress_ratio: int, db_session: AsyncSession) -> TaskStatus:
    if progress_ratio == 0:
        return TaskStatus.TODO
    elif progress_ratio == 100:
        return TaskStatus.DONE
    else:
        return TaskStatus.IN_PROGRESS

async def calculate_ratio(task_id: UUID, user_id: UUID, db_session: AsyncSession) -> int | None:
    total_subtasks = await fetch_subtasks(task_id, user_id, db_session)
    total_subtasks_cnt = len(total_subtasks)
    if total_subtasks_cnt == 0:
        return None
    completed_subtasks = [target_subtask
                          for target_subtask in total_subtasks
                          if target_subtask.is_complete]
    completed_subtasks_cnt = len(completed_subtasks)

    return round(completed_subtasks_cnt / total_subtasks_cnt * 100)
