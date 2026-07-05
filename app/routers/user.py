from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas.user import UserSchema, UserInDB, ResponseSchema
from cruds.user import add_user, fetch_user_by_email, authenticate_user
from sqlalchemy.ext.asyncio import AsyncSession
import db
import os
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from schemas.auth import TokenData, Token
from typing import Annotated
from models.user import User


router = APIRouter(prefix="/user")


@router.post(
    "/signup", response_model=ResponseSchema, status_code=status.HTTP_201_CREATED
)
async def signup_user(
    user: UserInDB, db_session: AsyncSession = Depends(db.get_db_session)
):
    try:
        new_user = await add_user(user, db_session)
        dict_user = UserSchema(
            user_id=new_user.user_id, user_name=new_user.user_name, email=new_user.email
        )
        return ResponseSchema(message="ユーザーの登録ができました。", user=dict_user)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=400, detail="ユーザーの登録に失敗しました。")


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: AsyncSession = Depends(db.get_db_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await fetch_user_by_email(email, db_session)
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: AsyncSession = Depends(db.get_db_session),
):
    user = await authenticate_user(
        form_data.username,  # メールアドレスを入れるためemailとしたいが決まりでusernameにしないといけないらしい
        form_data.password,
        db_session,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=ResponseSchema)
async def get_my_info(current_user: User = Depends(get_current_user)):
    dict_user = UserSchema(
        user_id=current_user.user_id,
        user_name=current_user.user_name,
        email=current_user.email,
    )
    return ResponseSchema(message="ユーザ情報を取得しました。", user=dict_user)
