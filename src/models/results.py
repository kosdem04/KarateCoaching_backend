from src.database import Base
from typing import List, Optional
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import Numeric
from decimal import Decimal
import uuid
from sqlalchemy.dialects.postgresql import UUID


class PlaceORM(Base):
    __tablename__ = 'places'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(10))

    results: Mapped[List["ResultORM"]] = relationship(
        "ResultORM",
        back_populates="place",
        cascade='all, delete'
    )



class ResultORM(Base):
    __tablename__ = 'results'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    student_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('student_profiles.student_id', ondelete='SET NULL')
    )
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('events.id', ondelete='SET NULL')
    )
    place_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('places.id', ondelete='SET NULL')
    )
    points_scored: Mapped[int]
    points_missed: Mapped[int]
    number_of_fights: Mapped[int]
    average_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False,
    )
    efficiency: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False,
    )
    event: Mapped["EventORM"] = relationship(
        "EventORM",
        back_populates="results"
    )
    place: Mapped["PlaceORM"] = relationship(
        "PlaceORM",
        back_populates="results"
    )

    student: Mapped["StudentProfileORM"] = relationship(
        "StudentProfileORM",
        back_populates="results"
    )
