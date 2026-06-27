from pydantic import BaseModel, Field
from datetime import date
import uuid
from models.tasks import Task


class UpdateAndCreateTaskSchema(BaseModel):
    task_name: str = Field(..., example="スキーマのコーディング")
    task_deadline: date = Field(..., example="2026-06-30")
    task_detail: str | None = Field(example="データの型の見直し")


class TaskSchema(UpdateAndCreateTaskSchema):
    task_id: uuid.UUID = Field(...)


class ResponseSchema(BaseModel):
    message: str = Field(..., description="操作に対するメッセージが入ります")
    task: TaskSchema = Field(..., description="作成されたタスクの詳細が入ります")
