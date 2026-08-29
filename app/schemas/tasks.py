import uuid
from datetime import date

from enums import TaskStatus
from pydantic import BaseModel, Field


class TaskStatusSchema(BaseModel):
    task_progress: TaskStatus = Field(default=TaskStatus.TODO)
    progress_ratio: int = Field(default=0)
    progress_comment: str | None = Field(max_length=30, example="Statusスキーマの変更")


class UpdateAndCreateTaskSchema(BaseModel):
    task_name: str = Field(..., example="スキーマのコーディング")
    task_deadline: date = Field(..., example="2026-06-30")
    task_detail: str | None = Field(example="データの型の見直し")
    task_status: TaskStatusSchema = Field(
        ...,
        example="task_progress: IN_PROGRESS,"
        "progress_ratio: 50%,"
        "progress_comment: Statusスキーマの変更",
    )


class TaskSchema(UpdateAndCreateTaskSchema):
    task_id: uuid.UUID = Field(...)


class ResponseSchema(BaseModel):
    message: str = Field(..., description="操作に対するメッセージが入ります")
