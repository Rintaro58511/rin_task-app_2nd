import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from enums import TaskStatus


class TaskStatusSchema(BaseModel):
    task_progress: TaskStatus = Field(default=TaskStatus.TODO)
    progress_ratio: int = Field(default=0)
    progress_comment: str | None = Field(
        max_length=30, json_schema_extra={"example": "Statusスキーマの変更"}
    )


class UpdateAndCreateTaskSchema(BaseModel):
    task_name: str = Field(..., json_schema_extra={"example": "スキーマのコーディング"})
    task_deadline: date = Field(..., json_schema_extra={"example": "2026-06-30"})
    task_detail: str | None = Field(json_schema_extra={"example": "データの型の見直し"})
    task_status: TaskStatusSchema = Field(
        ...,
        json_schema_extra={
            "example": "task_progress: IN_PROGRESS,"
            "progress_ratio: 50%,"
            "progress_comment: Statusスキーマの変更"
        },
    )


class TaskSchema(UpdateAndCreateTaskSchema):
    task_id: uuid.UUID = Field(...)
    changed_time: datetime = Field(...)


class ResponseSchema(BaseModel):
    message: str = Field(..., description="操作に対するメッセージが入ります")
