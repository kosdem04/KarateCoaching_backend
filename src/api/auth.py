from fastapi import APIRouter, HTTPException, status, Depends
from src.dependency.dependencies import SessionDep, AuthUserDep

from src.schemas.base import UserRegisterModel, UserLoginModel, Token
from src.requests.auth import AuthRequest
from src.security import create_access_token, generate_password
from src.models.groups import GroupORM
from src.models.events import EventORM
from src.utils.send_email import send_registration_email
from src.models.coaches import CoachProfileORM

router = APIRouter(
    prefix="/auth",
)


@router.post("/register",
            tags=["Пользователи"],
            summary="Регистрация нового пользователя",
         )
async def register(session: SessionDep, user: UserRegisterModel):
    password = generate_password()
    user_id = await AuthRequest.register(session, user, password=password)
    await AuthRequest.add_coach_role(session, user_id)
    await send_registration_email(user.email, password)
    return {"message": "Пользователь зарегистрирован"}


@router.post("/student/register/coach/{coach_id}",
            tags=["Пользователи"],
            summary="Регистрация нового ученика",
         )
async def student_register(session: SessionDep, user: UserRegisterModel, coach_id: str):
    password = generate_password()
    user_id = await AuthRequest.register(session, user, password=password)
    await AuthRequest.add_student_role(session, user_id)
    await AuthRequest.add_student_coach(session, student_id=user_id, coach_id=coach_id)
    await send_registration_email(user.email, password)
    return {"message": "Ученик зарегистрирован"}


@router.post("/login",
             tags=["Пользователи"],
             summary="Авторизация пользователя",
             response_model=Token)
async def login(session: SessionDep, data: UserLoginModel):
    user = await AuthRequest.authorization(session, data.email, data.password)
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


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
    user = await AuthRequest.get_user_data(session, user_id)
    return user


@router.get("/get_user_roles",
            tags=["Пользователи"],
            summary="Получение ролей пользователя",
            )
async def get_user_roles(session: SessionDep, user_id: AuthUserDep):
    roles = await AuthRequest.get_user_roles(session, user_id)
    return {"roles": roles}
