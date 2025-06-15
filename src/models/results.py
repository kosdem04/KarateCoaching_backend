from src.database import Base
from typing import List, Optional
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import Numeric, Enum
from decimal import Decimal
import uuid
from sqlalchemy.dialects.postgresql import UUID
import datetime
import enum


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
    sport_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('sport_types.id', ondelete='RESTRICT'),
    )
    sport_code: Mapped[Optional[str]] = mapped_column(String(50))
    age_category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('age_categories.id', ondelete='RESTRICT')
    )
    weight_category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('weight_categories.id', ondelete='SET NULL'),
        nullable=True
    )
    visited: Mapped[bool]


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

    place: Mapped["PlaceORM"] = relationship(
            "PlaceORM",
            back_populates="results"
        )
    age_category: Mapped["AgeCategoryORM"] = relationship(
        "AgeCategoryORM",
        back_populates="results"
    )
    weight_category: Mapped["WeightCategoryORM"] = relationship(
        "WeightCategoryORM",
        back_populates="results"
    )

    result_comments: Mapped[List["ResultCommentORM"]] = relationship(
        "ResultCommentORM",
        back_populates="result",
        cascade='all, delete'
    )

    __mapper_args__ = {
        "polymorphic_on": sport_code,
        "polymorphic_identity": "base"
    }


class ResultUserRole(enum.Enum):
    coach = "coach"
    student = "student"


class ResultCommentORM(Base):
    __tablename__ = 'result_comments'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    result_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('results.id', ondelete='CASCADE')
    )
    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    content: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime.datetime]

    author_role: Mapped[ResultUserRole] = mapped_column(Enum(ResultUserRole), nullable=False)


    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="result_comments"
    )

    result: Mapped["ResultORM"] = relationship(
        "ResultORM",
        back_populates="result_comments"
    )



class KarateKumiteResultORM(ResultORM):
    __tablename__ = 'karate_kumite_results'

    id: Mapped[uuid.UUID] = mapped_column(ForeignKey('results.id', ondelete='CASCADE'), primary_key=True)
    number_of_fights: Mapped[int]
    number_of_wins: Mapped[int]
    number_of_defeats: Mapped[int]
    points_scored: Mapped[int]
    points_missed: Mapped[int]
    average_score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    efficiency: Mapped[Decimal] = mapped_column(Numeric(5, 2))

    __mapper_args__ = {
        "polymorphic_identity": "karate-kumite"
    }