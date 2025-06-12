from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, or_
from sqlalchemy.orm import selectinload, joinedload

from src.models.students import StudentProfileORM
from src.models.users import UserORM, UserRoleORM, RoleORM
from src.security import hash_password, verify_password
from fastapi import HTTPException
from starlette import status
from src.schemas.base import UserRegisterModel
import datetime
import uuid


class AuthRequest:
    @classmethod
    async def register(cls, session: AsyncSession, user_data: UserRegisterModel, password:str):
        query = (
            select(UserORM)
            .where(UserORM.email == user_data.email)
        )
        user = await session.scalar(query)
        if not user:
            new_user = UserORM(
                first_name=user_data.first_name,
                patronymic=user_data.patronymic,
                last_name=user_data.last_name,
                email=user_data.email,
                password=hash_password(password),
                date_joined=datetime.datetime.now(datetime.UTC),
                img_url="https://s3.twcstorage.ru/414c6625-e8dd2907-0748-4c5c-8061-bbabd520cf1f/default-avatar.png",
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )


    @classmethod
    async def authorization(cls, session: AsyncSession, email: str, password: str):
        query = select(UserORM).where(UserORM.email == email)
        user = await session.scalar(query)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email пользователя",
            )
        elif not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль",
            )
        return user

    @classmethod
    async def get_user_data(cls, session: AsyncSession, user_id: str):
        query = (
            select(UserORM)
            .where(UserORM.id == user_id)
        )
        return await session.scalar(query)

    @classmethod
    async def get_user_roles(cls, session: AsyncSession, user_id: str):
        query = (
            select(UserRoleORM)
            .options(
                selectinload(UserRoleORM.role),
            )
            .where(UserRoleORM.user_id == user_id)
        )
        result_query = await session.execute(query)
        roles = result_query.scalars().all()
        return roles

    @classmethod
    async def add_coach_role(cls, session, user_id: str):
        query = (
            select(RoleORM.id)
            .where(RoleORM.code == "coach_role")
        )
        role_id = await session.scalar(query)
        session.add(UserRoleORM(
            user_id=user_id,
            role_id=role_id,
        ))
        await session.commit()

    @classmethod
    async def add_student_role(cls, session, user_id: str):
        query = (
            select(RoleORM.id)
            .where(RoleORM.code == "student_role")
        )
        role_id = await session.scalar(query)
        session.add(UserRoleORM(
            user_id=user_id,
            role_id=role_id,
        ))
        await session.commit()

    @classmethod
    async def add_student_coach(cls, session, student_id: str, coach_id: str):
        session.add(StudentProfileORM(
            student_id=student_id,
            coach_id=coach_id,
        ))
        await session.commit()

