import uuid
from typing import Annotated
from pydantic import (
    BaseModel, Field, EmailStr, Secret,
    SerializationInfo, PlainSerializer,
)

class SecretEmail(Secret[EmailStr]):
    def _display(self) -> str:
        return "***@***"

def dump_secret_email(
        v: SecretEmail, info: SerializationInfo
) -> str:
    if info.mode == "json":
        return str(v.get_secret_value())
    return str(v)

SecretEmailField = Annotated[
    SecretEmail,
    PlainSerializer(dump_secret_email),
]

class UserSchema(BaseModel):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_name: str = Field(..., example="佐藤 太郎")
    email: SecretEmailField = Field(..., example="example@gmail.com")


class UserInDB(UserSchema):
    hashed_password: str = Field(..., description="ハッシュ化されたパスワードが入ります")


class ResponseSchema(BaseModel):
    message: str = Field(..., description="操作に対するメッセージが入ります")
    user: UserSchema = Field(..., description="作成されたユーザーの詳細が入ります")