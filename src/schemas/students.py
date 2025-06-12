from pydantic import BaseModel, EmailStr
import datetime
from typing import Optional
from src.schemas.base import StudentModel
from src.schemas.base import PlaceModel
from src.schemas.events import EventModel
from src.schemas.groups import GroupModel
from uuid import UUID



class StudentProfileModel(BaseModel):
    student_data: Optional[StudentModel]
    coach_id: Optional[UUID]
    group_id: Optional[UUID]

    class Config:
        from_attributes = True



class StudentProfileProModel(BaseModel):
    student_data: Optional[StudentModel]
    coach_id: Optional[UUID]
    group: Optional[GroupModel]

    class Config:
        from_attributes = True


class StudentResultModel(BaseModel):
    event: Optional[EventModel]
    student_id: UUID
    place: Optional[PlaceModel]
    points_scored: int
    points_missed: int
    number_of_fights: int
    average_score: float
    efficiency: float

    class Config:
        from_attributes = True