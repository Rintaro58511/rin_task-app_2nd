from pydantic import BaseModel, Field
import uuid

class UserSchema(BaseModel):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_name: str = Field(..., example="佐藤 太郎")
    email: str = Field(..., example="example@gmail.com")


class UserInDB(UserSchema):
    hashed_password: str = Field(..., description="ハッシュ化されたパスワードが入ります")


class ResponseSchema(BaseModel):
    message: str = Field(..., description="操作に対するメッセージが入ります")
    user: UserSchema = Field(..., description="作成されたユーザーの詳細が入ります")