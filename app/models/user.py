from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Uuid, Bool
import uuid
from typing import List
from models.tasks import Base, Task

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    user_name: Mapped[str] = mapped_column(
        String(50),
        nullable = False,
    )
    email: Mapped[str] = mapped_column(
        String(100),
        nullable = False,
    )
    is_active: Mapped[bool] = mapped_column(
        Bool,
        nullable = False
    )
    tasks: Mapped[List["Task"]] = relationship(back_populates="user")