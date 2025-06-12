from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func, delete, asc
from sqlalchemy.orm import selectinload, joinedload
from src.models.users import UserORM, UserRoleORM, ResetPasswordCodeORM
from src.security import hash_password, verify_password
from fastapi import HTTPException
from starlette import status
from src.schemas.base import UserRegisterModel
import datetime



class UserRequest:

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
    async def update_user(cls, session: AsyncSession, user_id: str, **fields):
        query = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(**fields)
        )
        await session.execute(query)
        await session.commit()

    @classmethod
    async def delete_user(cls, session: AsyncSession, user_id: str):
        query = (
            delete(UserORM)
            .where(UserORM.id == user_id)
        )
        await session.execute(query)
        await session.commit()

    @classmethod
    async def is_code_in_db(cls, session: AsyncSession, code: str):
        query = (
            select(ResetPasswordCodeORM)
            .where(ResetPasswordCodeORM.code == code,
                   ResetPasswordCodeORM.is_used == False)
        )
        is_code = await session.scalar(query)
        return is_code

    @classmethod
    async def add_reset_code(cls, session: AsyncSession, code: str, email: str):
        user_query = (
            select(UserORM)
            .where(UserORM.email == email)
        )
        user = await session.scalar(user_query)
        session.add(ResetPasswordCodeORM(
            user_id=user.id,
            code=code,
        ))
        await session.commit()

    @classmethod
    async def code_use_true(cls, session: AsyncSession, code: str):
        query = (
            update(ResetPasswordCodeORM)
            .where(ResetPasswordCodeORM.code == code,
                   ResetPasswordCodeORM.is_used == False)
            .values(is_used=True)
        )
        await session.execute(query)
        await session.commit()

    @classmethod
    async def reset_password(cls, session: AsyncSession, code: str, password: str):
        code_query = (
            select(ResetPasswordCodeORM)
            .where(ResetPasswordCodeORM.code == code,
                   ResetPasswordCodeORM.is_used == False)
        )
        reset_code = await session.scalar(code_query)
        user_query = (
            update(UserORM)
            .where(UserORM.id == reset_code.user_id)
            .values(password=hash_password(password))
        )
        await session.execute(user_query)
        query = (
            update(ResetPasswordCodeORM)
            .where(ResetPasswordCodeORM.code == code,
                   ResetPasswordCodeORM.is_used == False)
            .values(is_used=True)
        )
        await session.execute(query)
        await session.commit()