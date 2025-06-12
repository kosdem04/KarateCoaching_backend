from fastapi import APIRouter
from src.api.events import router as events_router
from src.api.results import router as results_router
from src.api.auth import router as auth_router
from src.api.groups import router as groups_router
from src.api.students import router as students_router
from src.api.users import router as users_router



main_router = APIRouter()
main_router.include_router(results_router)
main_router.include_router(events_router)
main_router.include_router(auth_router)
main_router.include_router(groups_router)
main_router.include_router(students_router)
main_router.include_router(users_router)