from schemas.user import UserInDB
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def fetch_user_by_email(email: str,
                     db_session: AsyncSession) -> User:
    result = await db_session.execute(select(User).filter(User.email == email))
    target_user = result.scalars().first()

    return target_user

async def add_user(user: UserInDB,
                   db_session: AsyncSession) -> User:
    new_user = User(**user.model_dump())
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    return new_user
