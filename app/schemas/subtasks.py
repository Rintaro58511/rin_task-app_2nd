import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UpdateAndCreateSubTaskSchema(BaseModel):
    subtask_name: str = Field(..., max_length=30)
    is_complete: bool = Field(...)


class SubTaskSchema(UpdateAndCreateSubTaskSchema):
    subtask_id: uuid.UUID = Field(...)
    created_at: datetime = Field(...)


class ResponseSchema(BaseModel):
    message: str = Field(..., description="操作に対するメッセージが入ります")
