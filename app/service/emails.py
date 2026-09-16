from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import os
import smtplib
import ssl
from email.message import EmailMessage
import db
from models.tasks import Task
from models.user import User
from cruds.tasks import fetch_all_deadline_tasks, group_tasks_by_user
from schemas.tasks import ResponseSchema


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def create_email(user_name: str, user_email: str, tasks: list[Task]) -> EmailMessage:

    msg = EmailMessage()
    msg["Subject"] = f"{user_name}さん締め切りが近いまたは過ぎているタスクがあります。"

    body = f"{user_name}さん\n\n締め切りが近いまたは過ぎているタスクがあります。\n\n"

    for task in tasks:
        body += (
            "----------------------------------------\n"
            f"タスク名：{task.task_name}\n"
            f"タスク詳細：{task.task_detail}\n"
            f"進捗率：{task.progress_ratio}\n"
        )

    msg.set_content(body)

    msg["From"] = SMTP_USER
    msg["To"] = user_email

    return msg


def send_email(msg: EmailMessage) -> None:

    context = ssl.create_default_context()

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls(context=context)
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(msg)


async def create_and_send_email(
    user_name: str,
    user_email: str,
    tasks: list[Task],
) -> None:

    msg = create_email(user_name, user_email, tasks)

    await asyncio.to_thread(send_email, msg)

def group_tasks_by_user(all_deadline_tasks: list[tuple[Task, User]]):
    user_tasks = dict()
    for (task, user) in all_deadline_tasks:
        if user.user_id not in user_tasks:
            user_tasks[user.user_id] = { "user": user, "tasks": [task] }
        else: user_tasks[user.user_id]["tasks"].append(task)
    return user_tasks

async def send_deadline_notifications(
    db_session: AsyncSession,
) -> None:
    """明日までに締め切りを迎えるタスクがある場合にそれを持つユーザーにメールを送信する"""

    target_list = await fetch_all_deadline_tasks(db_session)

    deadline_task_by_user = group_tasks_by_user(target_list)

    for value in deadline_task_by_user.values():
        await create_and_send_email(value["user"].user_name, value["user"].email, value["tasks"])

    return None
