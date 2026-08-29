import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from enums import SubTaskPriority

if TYPE_CHECKING:
    from models.tasks import Task


class SubTask(Base):
    """サブタスク情報を管理するテーブル"""

    __tablename__ = "subtasks"
    subtask_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("tasks.task_id", ondelete="CASCADE"), nullable=False
    )
    subtask_name: Mapped[str] = mapped_column(String(30), nullable=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    priority: Mapped[SubTaskPriority] = mapped_column(
        SQLEnum(SubTaskPriority), default=SubTaskPriority.MEDIUM, nullable=False
    )
    task: Mapped["Task"] = relationship("Task", back_populates="subtasks")
