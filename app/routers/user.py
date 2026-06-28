from fastapi import APIRouter, status, HTTPException, Depends
from schemas.user import UserSchema, UserInDB, ResponseSchema
from cruds.user import add_user, fetch_user
from sqlalchemy.ext.asyncio import AsyncSession
from pwdlib import PasswordHash
import db
from uuid import UUID

router = APIRouter()
password_hash = PasswordHash.recommended()

@router.post("/signup", response_model = ResponseSchema, status_code = status.HTTP_201_CREATED)
async def signup_user(user: UserInDB,
                      db_session: AsyncSession = Depends(db.get_db_session)):
    try:
        hashed = password_hash.hash(user.password)
        user.hashed_password = hashed
        new_user = await add_user(user, db_session)
        dict_user = UserSchema(
        user_id = new_user.user_id,
        user_name = new_user.user_name,
        email = new_user.email
        )
        return ResponseSchema(message = "ユーザーの登録ができました。", user=dict_user)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail="ユーザーの登録に失敗しました。")

@router.post("/login", response_model = ResponseSchema)
async def login_user(user: UserInDB, db_session: AsyncSession = Depends(db.get_db_session)):
    login_user = await fetch_user(user.user_id, db_session)
    if login_user is None:
        raise HTTPException(status_code=400, detail="ユーザの情報が異なります。")
    if not password_hash.verify(user.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="ユーザの情報が異なります。")
    dict_user = UserSchema(
    user_id = login_user.user_id,
    user_name = login_user.user_name,
    email = login_user.email
    )
    return ResponseSchema(message = "ログイン完了", user=dict_user)
