from schemas.user import UserInDB
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


async def fetch_user_by_email(email: str, db_session: AsyncSession) -> User:
    """
    ユーザー情報をメールアドレスを元にデータベースから探す

    Args
        email(str): 探したいユーザーのメールアドレス
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        User: 探したいユーザーのユーザー情報
    """
    result = await db_session.execute(select(User).filter(User.email == email))
    target_user = result.scalars().first()

    return target_user


async def add_user(user: UserInDB, db_session: AsyncSession) -> User:
    """
    ユーザー情報をデータベースに追加する
    パスワードのハッシュ化はここで行う

    Args
        user(UserInDB): データベースに登録するのに必要なユーザーの情報
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        User: 追加したユーザー情報
    """
    hashed_password = password_hash.hash(user.hashed_password)

    user_data = user.model_dump()
    user_data["hashed_password"] = hashed_password
    new_user = User(**user_data)

    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    return new_user


async def authenticate_user(
    email: str, password: str, db_session: AsyncSession
) -> User:
    """
    ログイン情報（メールアドレス・パスワード）の検証を行う

    Args
        email(str): ログインフォームに入力されたメールアドレス
        password: ログインフォームに入力された平文パスワード
        db_session(AsyncSession): データベースの接続動作の依存性注入

    Return
        User | None: データベースに登録されているユーザー
    """
    logining_user = await fetch_user_by_email(email, db_session)

    if logining_user is None:
        return None

    if not password_hash.verify(password, logining_user.hashed_password):
        return None

    return logining_user
