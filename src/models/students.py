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
    level_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("sports_levels.id", ondelete="SET NULL"),
        nullable=True
    )
    weight: Mapped[Optional[str]] = mapped_column(String(5))
    first_coach: Mapped[Optional[str]] = mapped_column(String(100))
    medical_permit: Mapped[Optional[datetime.date]]


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

    level: Mapped[Optional["SportLevelORM"]] = relationship(
        "SportLevelORM",
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

    payments: Mapped[List["TrainingPaymentORM"]] = relationship(
        "TrainingPaymentORM",
        back_populates="student",
        passive_deletes=True
    )



class SportLevelORM(Base):
    __tablename__ = 'sports_levels'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(50), unique=True)


    students: Mapped[List["StudentProfileORM"]] = relationship(
        "StudentProfileORM",
        back_populates="level",
        passive_deletes=True
    )