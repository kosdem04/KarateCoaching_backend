from fastapi import APIRouter, HTTPException, status, Depends
from src.dependency.dependencies import SessionDep, AuthUserDep

from src.requests.coaches import CoachRequest
from src.requests.groups import GroupRequest
from src.requests.students import StudentRequest
from src.security import create_access_token
import src.schemas.groups as groups_schemas
import src.schemas.base as base_schemas

router = APIRouter(
    prefix="/groups",
)


async def get_current_coach_group(
    group_id : str,
    session: SessionDep,
    user_id: AuthUserDep,
):
    group = await GroupRequest.get_group_info(session, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    if group.coach_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return True


@router.get("/",
            tags=["Группы"],
            summary="Список всех групп тренера",
            response_model=list[groups_schemas.GroupModel]
         )
async def get_coach_groups(session: SessionDep, user_id: AuthUserDep):
    groups =  await CoachRequest.get_coach_groups(session, user_id)
    return groups


@router.get("/{group_id}/students",
            tags=["Группы"],
            summary="Список учеников в группе",
            response_model=list[base_schemas.StudentModel]
         )
async def get_students_in_group(
        session: SessionDep,
        group_id: str,
        coach_group: bool = Depends(get_current_coach_group)):
    students_orm =  await CoachRequest.get_students_in_group(session, group_id)
    students = [base_schemas.StudentModel.model_validate(r.student_data) for r in students_orm]
    return students



@router.get("/{group_id}",
            tags=["Группы"],
            summary="Информация о группе",
            response_model=groups_schemas.GroupModel
         )
async def get_group_info(
        session: SessionDep,
        group_id: str,
        coach_group: bool = Depends(get_current_coach_group)):
    group =  await GroupRequest.get_group_info(session, group_id)
    # group = groups_schemas.GroupModel.model_validate(result)
    return group



@router.post("/add",
            tags=["Группы"],
            summary="Добавление группы",
         )
async def add_group(session: SessionDep,
                         data: groups_schemas.AddGroupModel,
                         user_id: AuthUserDep):
    await GroupRequest.add_group(session=session,
                                 name=data.name,
                                 coach_id=user_id)
    return {"status": "ok"}


@router.patch(
    "/{group_id}",
    tags=["Группы"],
    summary="Частичное обновление группы",
)
async def edit_group(
    session: SessionDep,
    group_id: str,
    data: groups_schemas.EditGroupModel,
    user_id: AuthUserDep,
    coach_group: bool = Depends(get_current_coach_group)
):
    # Преобразуем только переданные поля в dict
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return {"status": "no fields to update"}

    await GroupRequest.update_group(session=session, group_id=group_id, **update_data)
    return {"status": "ok"}



@router.delete("/{group_id}",
            tags=["Группы"],
            summary="Удаление группы",
         )
async def delete_group(session: SessionDep,
                            group_id: str,
                            user_id: AuthUserDep,
                            coach_group: bool = Depends(get_current_coach_group)):
    await GroupRequest.delete_group(session, group_id)
    return {"status": "ok"}



@router.post("/{group_id}/add_student/{student_id}",
            tags=["Группы"],
            summary="Добавление ученика в группу",
         )
async def add_student_in_group(session: SessionDep,
                       group_id: str,
                       student_id: str,
                       user_id: AuthUserDep,
                       coach_group: bool = Depends(get_current_coach_group)):
    student = await StudentRequest.get_student_info(session, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    if student.group_id:
        raise HTTPException(status_code=403, detail="Ученик уже состоит в группе")
    else:
        await GroupRequest.add_student_in_group(session, group_id, student_id)
        return {"status": "ok"}



@router.delete("/{group_id}/add_student/{student_id}",
            tags=["Группы"],
            summary="Удаление ученика из группы",
         )
async def delete_student_from_group(session: SessionDep,
                       group_id: str,
                       student_id: str,
                       user_id: AuthUserDep,
                       coach_group: bool = Depends(get_current_coach_group)):
    student = await StudentRequest.get_student_info(session, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Ученик не найден")
    if not student.group_id:
        raise HTTPException(status_code=403, detail="Ученик не состоит в группе")
    else:
        await GroupRequest.delete_student_from_group(session, student_id)
        return {"status": "ok"}

