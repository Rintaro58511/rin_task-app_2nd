from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import db
from cruds.tasks import fetch_deadline_tasks, fetch_all_deadline_tasks, group_tasks_by_user
from routers.user import get_current_user
from schemas.tasks import ResponseSchema
from service.emails import create_and_send_email

router = APIRouter(prefix="/emails")


@router.post("/alert_deadline")
async def alert_deadline(
    current_user=Depends(get_current_user),
    db_session: AsyncSession = Depends(db.get_db_session),
) -> ResponseSchema:
    """明日までに締め切りを迎えるタスクがある場合にメールを送信する"""

    target_tasks = await fetch_deadline_tasks(current_user.user_id, db_session)

    await create_and_send_email(current_user.user_name, current_user.email, target_tasks)

    return ResponseSchema(message="メールを送信しました")
