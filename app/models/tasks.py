import uuid
from sqlalchemy import ForeignKey, String, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import date
from typing import Optional
from user import User

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_name: Mapped[str] = mapped_column(String(100), nullable=False)
    task_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    task_detail: Mapped[Optional[str]] = mapped_column(String(500))

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="tasks")