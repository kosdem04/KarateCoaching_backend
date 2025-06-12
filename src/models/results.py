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

    results: Mapped[List["KarateKumiteResultORM"]] = relationship(
        "KarateKumiteResultORM",
        back_populates="place",
        cascade='all, delete'
    )


class SportTypeORM(Base):
    __tablename__ = 'sport_types'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(100), unique=True)
    code: Mapped[str] = mapped_column(String(100), unique=True)

    results: Mapped[List["ResultORM"]] = relationship(
        "ResultORM",
        back_populates="sport_type",
        passive_deletes=True
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
    sport_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('sport_types.id', ondelete='RESTRICT'),
    )
    sport_code: Mapped[Optional[str]] = mapped_column(String(50))


    event: Mapped["EventORM"] = relationship(
        "EventORM",
        back_populates="results"
    )

    student: Mapped["StudentProfileORM"] = relationship(
        "StudentProfileORM",
        back_populates="results"
    )
    sport_type: Mapped["SportTypeORM"] = relationship(
        "SportTypeORM",
        back_populates="results"
    )

    __mapper_args__ = {
        "polymorphic_on": sport_code,
        "polymorphic_identity": "base"
    }



class KarateKumiteResultORM(ResultORM):
    __tablename__ = 'karate_kumite_results'

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey('results.id', ondelete='CASCADE'), primary_key=True)

    place_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('places.id', ondelete='SET NULL')
    )
    number_of_fights: Mapped[int]
    number_of_wins: Mapped[int]
    number_of_defeats: Mapped[int]
    points_scored: Mapped[int]
    points_missed: Mapped[int]
    average_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    efficiency: Mapped[Decimal] = mapped_column(Numeric(5, 2))

    place: Mapped["PlaceORM"] = relationship(
            "PlaceORM",
            back_populates="results"
        )

    __mapper_args__ = {
        "polymorphic_identity": "karate"
    }