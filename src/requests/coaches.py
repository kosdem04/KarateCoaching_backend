from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func, delete
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from src.models.groups import GroupORM
from src.models.students import StudentProfileORM
from fastapi import HTTPException
from starlette import status


class CoachRequest:
    @classmethod
    async def get_coach_groups(cls, session: AsyncSession, user_id: str):
        query = (
            select(GroupORM)
            .where(GroupORM.coach_id == user_id)
        )
        result_query = await session.execute(query)
        results = result_query.scalars().all()
        return results

    @classmethod
    async def get_students_in_group(cls, session: AsyncSession, group_id: str):
        query = (
            select(StudentProfileORM)
            .options(
                selectinload(StudentProfileORM.student_data),
            )
            .where(StudentProfileORM.group_id == group_id)
        )
        result_query = await session.execute(query)
        results = result_query.scalars().all()
        return results