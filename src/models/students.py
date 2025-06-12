from src.database import Base
from typing import List, Optional
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class StudentProfileORM(Base):
    __tablename__ = "student_profiles"
    # id: Mapped[str] = mapped_column(
    #     String(36),  # CHAR(36) по сути
    #     primary_key=True,
    #     default=lambda: str(uuid.uuid4())
    # )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    coach_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    group_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True
    )

    # связи
    student_data: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="student_profile",
        foreign_keys=[student_id]
    )

    coach: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="student",
        foreign_keys=[coach_id]
    )

    group: Mapped[Optional["GroupORM"]] = relationship(
        "GroupORM",
        back_populates="students"
    )

    results: Mapped[List["ResultORM"]] = relationship(
        "ResultORM",
        back_populates="student",
        passive_deletes=True
    )

    events: Mapped[List["EventORM"]] = relationship(
        "EventORM",
        back_populates="students",
        secondary="students_events"
    )