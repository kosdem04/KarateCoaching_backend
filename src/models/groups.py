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
        ForeignKey('users.id', ondelete='SET NULL')
    )
    coach: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="groups"
    )

    students: Mapped[List["StudentProfileORM"]] = relationship(
        "StudentProfileORM",
        back_populates="group",
        cascade='all, delete-orphan'
    )
