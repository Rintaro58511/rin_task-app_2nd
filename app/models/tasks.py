import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    UUID,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from enums import TaskStatus

if TYPE_CHECKING:
    from models.subtasks import SubTask
    from models.user import User


class Task(Base):
    """タスク情報を管理するテーブルモデル。"""

    __tablename__ = "tasks"
    task_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.user_id"), nullable=False, index=True
    )
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    task_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    task_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    task_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    task_progress: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False
    )
    progress_ratio: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    progress_comment: Mapped[str | None] = mapped_column(String(30), nullable=True)

    subtasks: Mapped[list["SubTask"]] = relationship(
        "SubTask",
        back_populates="task",
        cascade="all, delete-orphan",
    )
