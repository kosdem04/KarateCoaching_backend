from fastapi import APIRouter, HTTPException, Depends
from src.dependency.dependencies import SessionDep, AuthUserDep

import src.schemas.events as events_schemas
from src.requests.events import EventRequest
import src.schemas.base as base_schemas

from src.s3_storage import S3Client
from src.config import (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
                        S3_BUCKET_NAME, S3_ENDPOINT_URL, S3_REGION_NAME)

router = APIRouter(
    prefix="/events",
)


async def get_current_coach_event(
    event_id : str,
    session: SessionDep,
    user_id: AuthUserDep,
):
    event = await EventRequest.get_event(session, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    if event.coach_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return True


@router.get("/",
            tags=["Мероприятия"],
            summary="Просмотр всех мероприятий",
            response_model=list[events_schemas.EventModel]
         )
async def get_coach_events(session: SessionDep,
                               user_id: AuthUserDep):
    events = await EventRequest.get_coach_events(session, user_id)
    return events



@router.get("/types",
            tags=["Мероприятия"],
            summary="Просмотр всех типов мероприятий",
            response_model=list[base_schemas.TypeEventModel]
         )
async def get_event_types(session: SessionDep,
                               user_id: AuthUserDep):
    types = await EventRequest.get_event_types(session)
    # types = [base_schemas.TypeEventModel.model_validate(r) for r in types_orm]
    return types


@router.get("/{event_id}",
            tags=["Мероприятия"],
            summary="Информация о конкретном мероприятии",
            response_model=events_schemas.EventSimpleModel
         )
async def get_event(session: SessionDep,
                         event_id: str,
                         user_id: AuthUserDep,
                         coach_event: bool = Depends(get_current_coach_event)):
    event = await EventRequest.get_event(session, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено")
    return  event


@router.get("/{event_id}/students",
            tags=["Мероприятия"],
            summary="Список учеников на мероприятии",
            response_model=list[base_schemas.StudentModel]
         )
async def get_event_students(session: SessionDep,
                         event_id: str,
                         user_id: AuthUserDep,
                         coach_event: bool = Depends(get_current_coach_event)):
    students_orm = await EventRequest.get_event_students(session, event_id)
    students = [base_schemas.StudentModel.model_validate(r.student_data) for r in students_orm.students]
    return  students


@router.post("/{event_id}/{student_id}",
            tags=["Мероприятия"],
            summary="Регистрация ученика на мероприятие",
            # response_model=events_schemas.EventSimpleModel
         )
async def add_event_student(session: SessionDep,
                             event_id: str,
                             student_id: str,
                             user_id: AuthUserDep,
                             coach_event: bool = Depends(get_current_coach_event)):
    await EventRequest.add_event_student(
        session=session,
        event_id=event_id,
        student_id=student_id,
    )
    return {"status": "ok"}



@router.post("/add",
            tags=["Мероприятия"],
            summary="Добавление мероприятия",
         )
async def add_event(session: SessionDep,
                         data: events_schemas.AddEventModel,
                         user_id: AuthUserDep):
    await EventRequest.add_event(
        session=session,
        name=data.name,
        type_id=data.type_id,
        date_start=data.date_start,
        date_end=data.date_end,
        coach_id=user_id,
    )
    return {"status": "ok"}


@router.patch("/{event_id}",
            tags=["Мероприятия"],
            summary="Изменение мероприятия",
         )
async def update_event(session: SessionDep,
                           event_id: str,
                           data: events_schemas.EditEventModel,
                           user_id: AuthUserDep,
                            coach_event: bool = Depends(get_current_coach_event)):
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return {"status": "no fields to update"}

    await EventRequest.update_event(session=session, event_id=event_id, **update_data)
    return {"status": "ok"}



@router.delete("/{event_id}",
            tags=["Мероприятия"],
            summary="Удаление мероприятия",
         )
async def delete_event(session: SessionDep,
                            event_id: str,
                            user_id: AuthUserDep,
                            coach_event: bool = Depends(get_current_coach_event)):
    await EventRequest.delete_event(session, event_id)
    return {"status": "ok"}


@router.delete("/{event_id}/{student_id}",
            tags=["Мероприятия"],
            summary="Удаление ученика с мероприятия",
            # response_model=events_schemas.EventSimpleModel
         )
async def delete_student_from_event(session: SessionDep,
                             event_id: str,
                             student_id: str,
                             user_id: AuthUserDep,
                             coach_event: bool = Depends(get_current_coach_event)):
    await EventRequest.delete_student_from_event(
        session=session,
        event_id=event_id,
        student_id=student_id,
    )
    return {"status": "ok"}




