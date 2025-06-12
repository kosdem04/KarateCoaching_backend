from src.database import Base
from typing import List, Optional
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID


class CoachProfileORM(Base):
    __tablename__ = "coach_profiles"

    coach_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    # связи
    coach_data: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="coach_profile",
        foreign_keys=[coach_id]
    )

    events: Mapped[List["EventORM"]] = relationship(
        "EventORM",
        back_populates="coach",
        passive_deletes=True
    )
    groups: Mapped[List["GroupORM"]] = relationship(
        "GroupORM",
        back_populates="coach",
        passive_deletes=True
    )

    trainings: Mapped[List["TrainingORM"]] = relationship(
        "TrainingORM",
        back_populates="coach",
        passive_deletes=True
    )