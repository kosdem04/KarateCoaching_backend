from src.database import Base
from typing import List, Optional
import datetime
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import Numeric
from decimal import Decimal
import uuid
from sqlalchemy.dialects.postgresql import UUID


class EventORM(Base):
    __tablename__ = 'events'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(100))
    coach_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('coach_profiles.coach_id', ondelete='SET NULL')
    )
    type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('event_types.id', ondelete='SET NULL')
    )
    date_start: Mapped[datetime.date]
    date_end: Mapped[datetime.date]

    results: Mapped[List["ResultORM"]] = relationship(
        "ResultORM",
        back_populates="event",
        passive_deletes=True
    )
    coach: Mapped["CoachProfileORM"] = relationship(
        "CoachProfileORM",
        back_populates="events"
    )
    type: Mapped["EventTypeORM"] = relationship(
        "EventTypeORM",
        back_populates="events"
    )
    students: Mapped[List["StudentProfileORM"]] = relationship(
        "StudentProfileORM",
        back_populates="events",
        secondary="students_events"
    )



class EventTypeORM(Base):
    __tablename__ = 'event_types'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(100), unique=True)

    events: Mapped[List["EventORM"]] = relationship(
        "EventORM",
        back_populates="type",
        passive_deletes=True
    )


class StudentEventORM(Base):
    __tablename__ = 'students_events'

    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('student_profiles.student_id', ondelete='CASCADE'),
        primary_key=True
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('events.id', ondelete='CASCADE'),
        primary_key=True
    )
