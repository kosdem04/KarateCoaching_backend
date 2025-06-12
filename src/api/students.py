from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from src.dependency.dependencies import SessionDep, AuthUserDep

from src.requests.students import StudentRequest
from src.requests.users import UserRequest
from src.models.groups import GroupORM
import src.schemas.students as students_schemas
import src.schemas.base as base_schemas
import datetime
from src.s3_storage import S3Client
from src.config import (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
                        S3_BUCKET_NAME, S3_ENDPOINT_URL, S3_REGION_NAME)
from typing import Optional
import src.schemas.results as results_schemas


router = APIRouter(
    prefix="/students",
)

async def get_current_coach_student(
    student_id: str,
    session: SessionDep,
    user_id: AuthUserDep,
):
    student = await StudentRequest.get_student_info(session, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Спортсмен не найден")
    if student.coach_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return True



@router.get("/",
            tags=["Ученики"],
            summary="Просмотр учеников тренера",
            response_model=list[students_schemas.StudentProfileProModel]
         )
async def get_students_by_coach(session: SessionDep,
                                 user_id: AuthUserDep):
    students_orm = await StudentRequest.get_students_by_coach(session, user_id)
    students = [students_schemas.StudentProfileProModel.model_validate(r) for r in students_orm]
    return students



@router.get("/{student_id}",
            tags=["Ученики"],
            summary="Информация об ученике",
            response_model=students_schemas.StudentProfileModel
         )
async def get_student_info(
        session: SessionDep,
        student_id: str,
        user_id: AuthUserDep):
    print('!!!', student_id)
    student =  await StudentRequest.get_student_info(session, student_id)
    return student



@router.get("/{student_id}/results",
            tags=["Ученики"],
            summary="Получение результатов ученика",
            response_model=list[results_schemas.EventWithResultModel]
            # response_model=list[students_schemas.StudentResultModel]
         )
async def get_student_results(
        session: SessionDep,
        student_id: str,
        user_id: AuthUserDep):
    results =  await StudentRequest.get_student_results(session, student_id)
    return results


@router.get("/{student_id}/events",
            tags=["Ученики"],
            summary="Список мероприятий ученика",
            # response_model=events_schemas.EventSimpleModel
         )
async def get_student_events(session: SessionDep,
                         student_id: str,
                         user_id: AuthUserDep,
                         # coach_event: bool = Depends(get_current_coach_event)
                             ):
    events = await StudentRequest.get_student_events(session, student_id)
    return  events


@router.post("/add",
            tags=["Ученики"],
            summary="Добавление ученика",
         )
async def add_student(session: SessionDep,
                         user_id: AuthUserDep,
                        first_name: str = Form(...),
                        patronymic: str = Form(""),
                        last_name: str = Form(...),
                        date_of_birth: datetime.date = Form(...),
                        avatar: UploadFile = File(None),
                        ):
    s3_client = S3Client(
        access_key=AWS_ACCESS_KEY_ID,
        secret_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=S3_ENDPOINT_URL,
        bucket_name=S3_BUCKET_NAME,
        region_name=S3_REGION_NAME,
    )

    avatar_filename = None
    avatar_url = None
    if avatar:
        avatar_filename = await s3_client.upload_file(avatar)
        avatar_url = await s3_client.get_file_url(avatar_filename)
    await StudentRequest.add_student(session, first_name, patronymic, last_name, date_of_birth, avatar_url, user_id)
    return {"status": "ok"}




@router.patch("/{student_id}",
            tags=["Ученики"],
            summary="Изменение ученика",
         )
async def update_student(
    session: SessionDep,
    student_id: str,
    user_id: AuthUserDep,
    first_name: Optional[str] = Form(None),
    patronymic: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    date_of_birth: Optional[datetime.date] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    coach_student: bool = Depends(get_current_coach_student)
):
    s3_client = S3Client(
        access_key=AWS_ACCESS_KEY_ID,
        secret_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=S3_ENDPOINT_URL,
        bucket_name=S3_BUCKET_NAME,
        region_name=S3_REGION_NAME,
    )

    avatar_url = None
    if avatar:
        avatar_filename = await s3_client.upload_file(avatar)
        avatar_url = await s3_client.get_file_url(avatar_filename)

    # Формируем словарь обновляемых полей
    update_fields = {}
    if first_name is not None:
        update_fields['first_name'] = first_name
    if patronymic is not None:
        update_fields['patronymic'] = patronymic
    if last_name is not None:
        update_fields['last_name'] = last_name
    if date_of_birth is not None:
        update_fields['date_of_birth'] = date_of_birth
    if avatar_url is not None:
        update_fields['img_url'] = avatar_url

    if not update_fields:
        return {"status": "no fields to update"}


    await UserRequest.update_user(session=session, user_id=student_id, **update_fields)

    return {"status": "ok"}


@router.delete("/{student_id}",
            tags=["Ученики"],
            summary="Удаление ученика",
         )
async def delete_student(session: SessionDep,
                        student_id: str,
                        user_id: AuthUserDep,
                        coach_student: bool = Depends(get_current_coach_student)):
    await UserRequest.delete_user(session, user_id=student_id)
    return {"status": "ok"}

