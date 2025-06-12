from fastapi import APIRouter, HTTPException, Depends
from src.dependency.dependencies import SessionDep, AuthUserDep


import src.models.results as results_models
from src.requests.results import ResultRequest
import src.schemas.results as results_schemas
import src.schemas.base as base_schemas

router = APIRouter(
    prefix="/results",
)

@router.get("/places/",
            tags=["Места"],
            summary="Просмотр всех мест",
            response_model=list[results_schemas.PlaceModel]

         )
async def get_places(session: SessionDep):
    places = await ResultRequest.get_places(session)
    return places



@router.get("/",
            tags=["Результаты"],
            summary="Просмотр всех результатов",
            response_model=list[results_schemas.EventWithResultModel]
         )
async def get_user_results(session: SessionDep,
                               user_id: AuthUserDep):
    results = await ResultRequest.get_results(session, user_id)
    return results


@router.get("/{result_id}",
            tags=["Результаты"],
            summary="Информация о конкретном результате",
            response_model=base_schemas.ResulSimpleModel
         )
async def get_result(session: SessionDep,
                        result_id: str,
                        user_id: AuthUserDep):
    result = await ResultRequest.get_result(session, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Результат не найден")
    return  result


@router.post("/add",
            tags=["Результаты"],
            summary="Добавление результата",
         )
async def add_result(session: SessionDep,
                         data: results_schemas.AddResultModel,
                         user_id: AuthUserDep):
    await ResultRequest.add_result(
        session=session,
        event_id=data.event_id,
        student_id=data.student_id,
        place_id=data.place_id,
        points_scored=data.points_scored,
        points_missed=data.points_missed,
        number_of_fights=data.number_of_fights,
    )
    return {"status": "ok"}


@router.patch("/{result_id}",
            tags=["Результаты"],
            summary="Изменение результата",
         )
async def update_result(session: SessionDep,
                           result_id: str,
                           data: results_schemas.EditResultModel,
                           user_id: AuthUserDep):
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return {"status": "no fields to update"}
    await ResultRequest.update_result(session=session, result_id=result_id, **update_data)
    return {"status": "ok"}


@router.delete("/{result_id}",
            tags=["Результаты"],
            summary="Удаление результата",
         )
async def delete_result(session: SessionDep,
                        result_id: str,
                        user_id: AuthUserDep):
    await ResultRequest.delete_result(session, result_id)
    return {"status": "ok"}
