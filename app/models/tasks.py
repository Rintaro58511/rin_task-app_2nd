from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text, Uuid, Date
import uuid
from datetime import date


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"
    task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    task_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    task_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    task_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
