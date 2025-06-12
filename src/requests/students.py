import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func, delete, asc
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from src.models.students import StudentProfileORM
from fastapi import HTTPException
from starlette import status
from src.models.users import UserORM
from src.config import DEFAULT_AVATAR
from src.models.results import ResultORM, PlaceORM
from src.models.events import EventORM


class StudentRequest:
    @classmethod
    async def get_student_info(cls, session: AsyncSession, student_id: str):
        query = (
            select(StudentProfileORM)
            .options(
                selectinload(StudentProfileORM.student_data),
            )
            .where(StudentProfileORM.student_id == student_id)
        )
        result_query = await session.execute(query)
        result = result_query.scalar()
        return result

    @classmethod
    async def get_students_by_coach(cls, session: AsyncSession, coach_id: str):
        query = (
            select(StudentProfileORM)
            .options(
                selectinload(StudentProfileORM.student_data),
                selectinload(StudentProfileORM.group),
            )
            .where(StudentProfileORM.coach_id == coach_id)
        )
        result_query = await session.execute(query)
        results = result_query.scalars().all()
        return results

    @classmethod
    async def get_student_events(cls, session: AsyncSession, student_id: str):
        query = (
            select(StudentProfileORM)
            .options(
                selectinload(StudentProfileORM.events)
                .selectinload(EventORM.type)
            )
            .where(StudentProfileORM.student_id == student_id)
        )
        student: StudentProfileORM | None = await session.scalar(query)
        if not student:
            return []
        return sorted(student.events, key=lambda e: e.date_start, reverse=True)

    @classmethod
    async def add_student(cls, session, first_name: str, patronymic: str, last_name: str,
                            date_of_birth: datetime.date, avatar_url: str | None, coach_id: str):

        img_url = avatar_url or DEFAULT_AVATAR
        query = (
            select(UserORM)
            .options(
                selectinload(UserORM.student_profile),
            )
            .where(UserORM.first_name == first_name,
                   UserORM.patronymic == patronymic,
                   UserORM.last_name == last_name,
                   UserORM.date_of_birth == date_of_birth,
                   StudentProfileORM.coach_id == coach_id)
        )
        student = await session.scalar(query)
        if not student:
            new_user = UserORM(
                first_name=first_name,
                patronymic=patronymic,
                last_name=last_name,
                date_of_birth=date_of_birth,
                img_url=img_url,
            )
            session.add(new_user)
            await session.flush()  # получить ID до использования

            session.add(StudentProfileORM(
                student_id=new_user.id,
                coach_id=coach_id,
            ))
            await session.commit()
        elif not student.student_profile:
            session.add(StudentProfileORM(
                student_id=student.id,
                coach_id=coach_id,
            ))
            await session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такой ученик уже существует"
            )



    @classmethod
    async def get_student_results(cls, session: AsyncSession, student_id: str):
        # query = (
        #     select(ResultORM)
        #     .join(ResultORM.event)
        #     .options(
        #         selectinload(ResultORM.event)
        #         .options(
        #             selectinload(EventORM.type),
        #         ),
        #         selectinload(ResultORM.place),
        #     )
        #     .where(ResultORM.student_id == student_id)
        #     .order_by(asc(EventORM.date_start))
        # )

        query = (
            select(EventORM)
            .join(ResultORM, EventORM.results)
            .options(
                contains_eager(EventORM.results)
                .options(
                    selectinload(ResultORM.place),
                    selectinload(ResultORM.student)
                    .options(selectinload(StudentProfileORM.student_data))
                )
            )
            .where(ResultORM.student_id == student_id)
            .order_by(desc(EventORM.date_start))
        )
        result_query = await session.execute(query)
        results = result_query.unique().scalars().all()
        return results