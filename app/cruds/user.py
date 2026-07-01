from schemas.user import UserInDB
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


async def fetch_user_by_email(email: str, db_session: AsyncSession) -> User:
    result = await db_session.execute(select(User).filter(User.email == email))
    target_user = result.scalars().first()

    return target_user


async def add_user(user: UserInDB, db_session: AsyncSession) -> User:
    hashed = password_hash.hash(user.hashed_password)
    user.hashed_password = hashed
    new_user = User(**user.model_dump())
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    return new_user


async def authenticate_user(
    email: str, password: str, db_session: AsyncSession
) -> User:
    logining_user = await fetch_user_by_email(email, db_session)
    if logining_user is None:
        return None
    if not password_hash.verify(password, logining_user.hashed_password):
        return None
    return logining_user
