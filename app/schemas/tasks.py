from pydantic import BaseModel, Field, computed_field
from datetime import date
import uuid
from enums import TaskStatus


class UpdateAndCreateTaskSchema(BaseModel):
    task_name: str = Field(..., example="スキーマのコーディング")
    task_deadline: date = Field(..., example="2026-06-30")
    task_detail: str | None = Field(example="データの型の見直し")
    task_status: TaskStatus = Field(default=TaskStatus.TODO)


class TaskSchema(UpdateAndCreateTaskSchema):
    task_id: uuid.UUID = Field(...)

    @property
    @computed_field
    def is_expired(self) -> bool:
        return self.task_deadline < date.today()

    model_config = {"from_attributes": True}


class ResponseSchema(BaseModel):
    message: str = Field(..., description="操作に対するメッセージが入ります")
    task: TaskSchema = Field(..., description="作成されたタスクの詳細が入ります")
