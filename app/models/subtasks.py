from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    UUID,
    ForeignKey,
    Boolean,
    String,
    DateTime,
)
import uuid
from datetime import datetime
from db import Base

class SubTask(Base):
    """サブタスク情報を管理するテーブル"""

    __tablename__ = "subtasks"
    subtask_id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("tasks.task_id", ondelete="CASCADE"), nullable=False
    )
    subtask_name: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    is_complete: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] =  mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    task: Mapped["Task"] = relationship("Task", back_populates="subtasks")