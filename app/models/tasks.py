from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, UUID, Date, ForeignKey, Enum as SQLEnum
import uuid
from datetime import date
from db import Base
from enums import TaskStatus


class Task(Base):
    __tablename__ = "tasks"
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4
    )
    task_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    task_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    task_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("users.user_id"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    task_status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False
    )
