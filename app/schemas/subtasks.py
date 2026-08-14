from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class UpdateAndCreateSubTaskSchema(BaseModel):
    subtask_name: str = Field(...)
    is_complete: bool = Field(...)


class SubTaskSchema(UpdateAndCreateSubTaskSchema):
    subtask_id: uuid.UUID = Field()
    created_at: datetime = Field()
