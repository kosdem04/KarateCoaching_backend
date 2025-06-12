from enum import unique

from src.database import Base
from typing import List, Optional
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID



class OrganizationORM(Base):
    __tablename__ = 'organizations'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(100), unique=True)
    subdomain: Mapped[str] = mapped_column(String(50), unique=True)
    is_active : Mapped[bool]
    created_at : Mapped[datetime.date]

    users: Mapped[List["UserORM"]] = relationship(
        "UserORM",
        back_populates="organization",
        passive_deletes=True
    )


class UserORM(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('organizations.id', ondelete='CASCADE')
    )
    last_name: Mapped[str] = mapped_column(String(64))
    first_name: Mapped[str] = mapped_column(String(30))
    patronymic: Mapped[str] = mapped_column(String(30), nullable=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    password: Mapped[str] = mapped_column(String(150))
    date_joined: Mapped[datetime.date]
    date_of_birth: Mapped[datetime.date] = mapped_column(nullable=True)
    img_url: Mapped[str] = mapped_column(String(1000))

    organization: Mapped["OrganizationORM"] = relationship(
        "OrganizationORM",
        back_populates="users"
    )
    roles: Mapped[List["RoleORM"]] = relationship(
        "RoleORM",
        back_populates="users",
        secondary="user_roles"
    )
    reset_password_codes: Mapped[List["ResetPasswordCodeORM"]] = relationship(
        "ResetPasswordCodeORM",
        back_populates="user",
        cascade='all, delete'
    )

    # один-к-одному: если пользователь — ученик
    student_profile: Mapped[Optional["StudentProfileORM"]] = relationship(
        "StudentProfileORM",
        back_populates="student_data",
        uselist=False,
        foreign_keys="[StudentProfileORM.student_id]"
    )
    coach_profile: Mapped[Optional["CoachProfileORM"]] = relationship(
        "CoachProfileORM",
        back_populates="coach_data",
        uselist=False,
        foreign_keys="[CoachProfileORM.coach_id]"
    )

    # один-ко-многим: если пользователь — тренер
    student: Mapped[List["StudentProfileORM"]] = relationship(
        "StudentProfileORM",
        back_populates="coach",
        foreign_keys="[StudentProfileORM.coach_id]"
    )



class RoleORM(Base):
    __tablename__ = 'roles'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    name: Mapped[str] = mapped_column(String(50), unique=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)

    user_roles: Mapped[List["UserRoleORM"]] = relationship(
        "UserRoleORM",
        back_populates="role",
        cascade='all, delete'
    )

    users: Mapped[List["UserORM"]] = relationship(
        "UserORM",
        back_populates="roles",
        secondary="user_roles"
    )



class UserRoleORM(Base):
    __tablename__ = 'user_roles'

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'),
                                               primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)

    role: Mapped["RoleORM"] = relationship(
        "RoleORM",
        back_populates="user_roles"
    )


class ResetPasswordCodeORM(Base):
    __tablename__ = 'reset_password_codes'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),  # нативный тип UUID PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # передаём функцию, не вызываем
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    code: Mapped[str] = mapped_column(String(6))
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())
    is_used: Mapped[bool] =  mapped_column(default=False)

    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="reset_password_codes"
    )


