from pydantic import BaseModel, Field
from datetime import datetime

class UpdateAndCreateTaskSchema(BaseModel):
    task_name: str = Field(..., example="スキーマのコーディング")
    task_deadline: datetime = Field(..., example="2026-06-30T00:00:00")
    task_detail: str = Field(default=None)

class TaskSchema(UpdateAndCreateTaskSchema):
    task_id: int = Field(...)

class ResponseSchema(BaseModel):
    message: str = Field(..., description="操作に対するメッセージが入ります")
    task: TaskSchema = Field(..., description="作成されたタスクの詳細が入ります")