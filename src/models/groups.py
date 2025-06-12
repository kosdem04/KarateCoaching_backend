from src.database import Base
from typing import List, Optional
import datetime
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import Numeric
from decimal import Decimal
import uuid
from sqlalchemy.dialects.postgresql import UUID


class GroupORM(Base):
    __tablename__ = 'groups'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(100))
    coach_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('coach_profiles.coach_id', ondelete='SET NULL')
    )

    coach: Mapped["CoachProfileORM"] = relationship(
        "CoachProfileORM",
        back_populates="groups"
    )

    students: Mapped[List["StudentProfileORM"]] = relationship(
        "StudentProfileORM",
        back_populates="group",
        cascade='all, delete-orphan'
    )

    trainings: Mapped[List["TrainingORM"]] = relationship(
        "TrainingORM",
        back_populates="group",
        cascade='all, delete-orphan'
    )


class TrainingORM(Base):
    __tablename__ = 'trainings'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(100))
    group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('groups.id', ondelete='CASCADE')
    )
    coach_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('coach_profiles.coach_id', ondelete='CASCADE')
    )
    date: Mapped[datetime.date]
    start_time: Mapped[datetime.time]
    end_time: Mapped[datetime.time]

    coach: Mapped["CoachProfileORM"] = relationship(
        "CoachProfileORM",
        back_populates="trainings"
    )

    group: Mapped["GroupORM"] = relationship(
        "GroupORM",
        back_populates="trainings"
    )


class AttendanceStatusORM(Base):
    __tablename__ = 'attendance_statuses'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(100), unique=True)

    attendance_list: Mapped[List["AttendanceORM"]] = relationship(
        "AttendanceORM",
        back_populates="status",
        passive_deletes=True
    )


class AttendanceORM(Base):
    __tablename__ = 'attendance'

    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('student_profiles.student_id', ondelete='CASCADE'),
        primary_key=True
    )

    training_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trainings.id", ondelete="CASCADE"),
        primary_key=True
    )
    status_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('attendance_statuses.id', ondelete='CASCADE')
    )

    status: Mapped["AttendanceStatusORM"] = relationship(
        "AttendanceStatusORM",
        back_populates="attendance_list"
    )


