import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import UUID, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base

if TYPE_CHECKING:
    from models.tasks import Task


class User(Base):
    """ユーザーの情報を管理するテーブル"""

    __tablename__ = "users"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="user", cascade="all, delete-orphan"
    )
