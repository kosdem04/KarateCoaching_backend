from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from src.dependency.dependencies import SessionDep, AuthUserDep
from src.requests.students import StudentRequest
from src.requests.users import UserRequest
import datetime
from src.s3_storage import S3Client
from src.config import (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
                        S3_BUCKET_NAME, S3_ENDPOINT_URL, S3_REGION_NAME)
from typing import Optional
from src.security import hash_password, generate_reset_code
import src.schemas.users as users_schemas
from src.utils.send_email import send_reset_password_email


router = APIRouter(
    prefix="/users",
)


async def is_access_to_edit_user(
    user_id: str,
    session: SessionDep,
    user_auth_id: AuthUserDep,
):
    student = await StudentRequest.get_student_info(session, user_id)
    if user_id == user_auth_id:
        return True
    elif not student:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    elif student.coach_id != user_auth_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return True


@router.get("/get_user",
            tags=["Пользователи"],
            summary="Получение информации о пользователе",
            )
async def get_user(user_id: AuthUserDep):
    return {"user_id": user_id}



@router.get("/get_user_data",
            tags=["Пользователи"],
            summary="Получение данных о пользователе",
            )
async def get_user_data(session: SessionDep, user_id: AuthUserDep):
    user = await UserRequest.get_user_data(session, user_id)
    return user


@router.get("/get_user_roles",
            tags=["Пользователи"],
            summary="Получение ролей пользователя",
            )
async def get_user_roles(session: SessionDep, user_id: AuthUserDep):
    roles = await UserRequest.get_user_roles(session, user_id)
    return {"roles": roles}


@router.post("/password/forgot",
            tags=["Пользователи"],
            summary="Генерация кода для восстановления пароля",
         )
async def generate_reset_password_code(session: SessionDep, data: users_schemas.GenerateResetPasswordCodeModel):
    for _ in range(10):
        code = generate_reset_code()
        exists = await UserRequest.is_code_in_db(session=session,
                                 code=code)
        if not exists:
            await UserRequest.add_reset_code(session=session,
                                         code=code,
                                         email=data.email)
            await send_reset_password_email(to_email=data.email, code=code)
            return {"status": "ok"}

    raise HTTPException(status_code=500, detail="Не удалось сгенерировать уникальный код. Попробуйте позже.")



@router.post("/password/reset",
            tags=["Пользователи"],
            summary="Добавление нового пароля",
         )
async def reset_password(session: SessionDep, data: users_schemas.ResetPasswordModel):
    # проверить, есть ли такой код в бд и он не использован
    code = await UserRequest.is_code_in_db(session=session,
                                             code=data.code)
    if not code:
        raise HTTPException(status_code=400, detail="Неверный код")
    # проверить, прошло ли больше 24 часов, и если да, то не менять пароль и сделать код использованным
    if code.created_at + datetime.timedelta(hours=24) < datetime.datetime.now():
        await UserRequest.code_use_true(session=session,
                                         code=data.code)
        raise HTTPException(status_code=400, detail="Истёк срок действия кода")
    # проверить, совпадают ли пароли
    if data.new_password != data.repeat_new_password:
        raise HTTPException(status_code=400, detail="Пароли не совпадают")
    # сменить пароля и сделать код использованным
    await UserRequest.reset_password(session=session,
                                     code=data.code,
                                     password=data.new_password)
    return {"status": "ok"}



@router.patch("/update/{user_id}",
            tags=["Пользователи"],
            summary="Изменение пользователя",
         )
async def update_user(
    session: SessionDep,
    user_id: str,
    user_auth_id: AuthUserDep,
    first_name: Optional[str] = Form(None),
    patronymic: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    date_of_birth: Optional[datetime.date] = Form(None),
    avatar: Optional[UploadFile] = File(None),
        password: Optional[str] = Form(None),
        password_repeat: Optional[str] = Form(None),
        is_access: bool = Depends(is_access_to_edit_user)
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
    if phone_number is not None:
        update_fields['phone_number'] = phone_number
    if password is not None:
        if password == password_repeat:
            update_fields['password'] = hash_password(password)
        else:
            raise HTTPException(status_code=400, detail="Пароли не совпадают")

    if not update_fields:
        return {"status": "no fields to update"}

    await UserRequest.update_user(session=session, user_id=user_id, **update_fields)

    return {"status": "ok"}


@router.delete("/delete/{user_id}",
            tags=["Пользователи"],
            summary="Удаление пользователя",
         )
async def delete_user(session: SessionDep,
                        user_id: str,
                        user_auth_id: AuthUserDep,
                        is_access: bool = Depends(is_access_to_edit_user)):
    await UserRequest.delete_user(session, user_id=user_id)
    return {"status": "ok"}