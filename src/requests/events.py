import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, delete
from sqlalchemy.orm import selectinload, joinedload

from src.models.events import EventORM, EventTypeORM, StudentEventORM
from fastapi import HTTPException
from starlette import status
from uuid import UUID


from src.models.students import StudentProfileORM


class EventRequest:
    @classmethod
    async def get_coach_events(cls, session: AsyncSession, coach_id: str):
        query = (
            select(EventORM)
            .options(
                selectinload(EventORM.type),
            )
            .where(EventORM.coach_id == coach_id)
            .order_by(desc(EventORM.date_start))
        )
        result_query = await session.execute(query)
        results = result_query.scalars().all()
        return results

    @classmethod
    async def get_event_students(cls, session: AsyncSession, event_id: str):
        query = (
            select(EventORM)
            .options(
                selectinload(EventORM.students)
                .options(
                    selectinload(StudentProfileORM.student_data),
                ),
            )
            .where(EventORM.id == event_id)
        )
        result_query = await session.execute(query)
        results = result_query.scalar()
        return results

    @classmethod
    async def get_event(cls, session: AsyncSession, event_id: str):
        query = (
            select(EventORM)
            .where(EventORM.id == event_id)
        )
        result = await session.scalar(query)
        return result

    @classmethod
    async def get_event_types(cls, session: AsyncSession):
        query = (
            select(EventTypeORM)
        )
        result_query = await session.execute(query)
        results = result_query.scalars().all()
        return results


    @classmethod
    async def add_event(cls, session, name: str, type_id: UUID,
                        date_start: datetime.date, date_end: datetime.date, coach_id: str):
        query = (
            select(EventORM)
            .where(EventORM.name == name,
                   EventORM.type_id == type_id,
                   EventORM.date_start == date_start,
                   EventORM.date_end == date_end,
                   EventORM.coach_id == coach_id)
        )
        event = await session.scalar(query)
        if not event:
            session.add(EventORM(
                name=name,
                type_id=type_id,
                date_start=date_start,
                date_end=date_end,
                coach_id=coach_id,
            ))
            await session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такое мероприятие уже есть"
            )

    @classmethod
    async def add_event_student(cls, session, event_id: str, student_id: str):
        query = (
            select(StudentEventORM)
            .where(StudentEventORM.event_id == event_id,
                   StudentEventORM.student_id == student_id)
        )
        student_in_event = await session.scalar(query)
        if not student_in_event:
            session.add(StudentEventORM(
                event_id=event_id,
                student_id=student_id,
            ))
            await session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Спортсмен уже зарегистрирован на это мероприятие"
            )

    @classmethod
    async def update_event(cls, session, event_id: str, **fields):
        query = (
            update(EventORM)
            .where(EventORM.id == event_id)
            .values(**fields)
        )
        await session.execute(query)
        await session.commit()


    @classmethod
    async def delete_event(cls, session: AsyncSession, event_id: str):
        query = (
            delete(EventORM)
            .where(EventORM.id == event_id)
        )
        await session.execute(query)
        await session.commit()

    @classmethod
    async def delete_student_from_event(cls, session, event_id: str, student_id: str):
        query = (
            delete(StudentEventORM)
            .where(StudentEventORM.student_id == student_id,
                   StudentEventORM.event_id == event_id)
        )
        await session.execute(query)
        await session.commit()