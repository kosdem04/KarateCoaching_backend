from src.database import Base
from typing import List, Optional
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Numeric, Enum
from decimal import Decimal


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
    # 🧾 Реквизиты для ЮKassa (или другого провайдера)
    payment_provider: Mapped[str] = mapped_column(String(50), nullable=True)  # например, "yookassa"
    payment_account_id: Mapped[str] = mapped_column(String(100), nullable=True)  # shop_id
    payment_secret_key: Mapped[str] = mapped_column(String(200), nullable=True)  # secret key
    tax_system_code: Mapped[int] = mapped_column(nullable=True)  # код налогообложения для чеков

    users: Mapped[List["UserORM"]] = relationship(
        "UserORM",
        back_populates="organization",
        passive_deletes=True
    )

    student_payments: Mapped[List["TrainingPaymentORM"]] = relationship(
        "TrainingPaymentORM",
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
    gender_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('genders.id', ondelete='SET NULL')
    )

    organization: Mapped["OrganizationORM"] = relationship(
        "OrganizationORM",
        back_populates="users"
    )
    gender: Mapped["GenderORM"] = relationship(
        "GenderORM",
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
    result_comments: Mapped[List["ResultCommentORM"]] = relationship(
        "ResultCommentORM",
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


class TrainingPaymentORM(Base):
    __tablename__ = 'training_payments'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL")
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("student_profiles.student_id", ondelete="SET NULL"),
        nullable=True
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(30))  # например, 'pending', 'succeeded', 'failed'
    description: Mapped[str] = mapped_column(String(255))
    external_payment_id: Mapped[str] = mapped_column(String(100))  # id из ЮKassa
    created_at: Mapped[datetime.datetime]
    email: Mapped[str] = mapped_column(String(254), nullable=True)  # email ученика для чека

    student: Mapped["StudentProfileORM"] = relationship(
        "StudentProfileORM",
        back_populates="payments"
    )

    organization: Mapped["OrganizationORM"] = relationship(
        "OrganizationORM",
        back_populates="student_payments"
    )

