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


class GenderORM(Base):
    __tablename__ = 'genders'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(20), unique=True)  # Например: "Мужчины", "Женщины"

    users: Mapped[List["UserORM"]] = relationship(
        "UserORM",
        back_populates="gender",
        cascade='all, delete'
    )
    age_categories: Mapped[List["AgeCategoryORM"]] = relationship(
        "AgeCategoryORM",
        back_populates="gender",
        cascade='all, delete'
    )
    weight_categories: Mapped[List["WeightCategoryORM"]] = relationship(
        "WeightCategoryORM",
        back_populates="gender",
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
    age_categories: Mapped[List["AgeCategoryORM"]] = relationship(
        "AgeCategoryORM",
        back_populates="sport_type",
        passive_deletes=True
    )



class AgeCategoryORM(Base):
    __tablename__ = 'age_categories'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[Optional[str]] = mapped_column(String(50))  # Например: "14-15 лет", "18+", можно оставить пустым
    min_age: Mapped[int]
    max_age: Mapped[Optional[int]]  # None — если нет верхней границы
    sport_type_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('sport_types.id', ondelete='CASCADE')
    )
    gender_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('genders.id', ondelete='CASCADE')
    )

    gender: Mapped["GenderORM"] = relationship(
        "GenderORM",
        back_populates="age_categories"
    )
    sport_type: Mapped["SportTypeORM"] = relationship(
        "SportTypeORM",
        back_populates="age_categories"
    )
    weight_categories: Mapped[List["WeightCategoryORM"]] = relationship(
        "WeightCategoryORM",
        back_populates="age_category",
        cascade="all, delete-orphan"
    )
    results: Mapped[List["ResultORM"]] = relationship(
        "ResultORM",
        back_populates="age_category",
        cascade="all, delete-orphan"
    )


class WeightCategoryORM(Base):
    __tablename__ = 'weight_categories'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[Optional[str]] = mapped_column(String(50))  # Например: "до 60 кг"
    max_weight: Mapped[Optional[int]]  # None — если не используется
    age_category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('age_categories.id', ondelete='CASCADE')
    )
    gender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('genders.id', ondelete='CASCADE')
    )

    gender: Mapped["GenderORM"] = relationship(
        "GenderORM",
        back_populates="weight_categories"
    )
    age_category: Mapped["AgeCategoryORM"] = relationship(
        "AgeCategoryORM",
        back_populates="weight_categories"
    )
    results: Mapped[List["ResultORM"]] = relationship(
        "ResultORM",
        back_populates="weight_category",
        cascade="all, delete-orphan"
    )

