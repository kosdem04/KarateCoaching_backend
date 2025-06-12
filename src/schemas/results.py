from pydantic import BaseModel
from typing import Optional
import datetime
from src.schemas.base import StudentModel
from src.schemas.students import StudentProfileModel
from uuid import UUID


class PlaceModel(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class AddResultModel(BaseModel):
    event_id: UUID
    student_id: UUID
    place_id: UUID
    points_scored: int
    points_missed: int
    number_of_fights: int

    class Config:
        from_attributes = True



class EditResultModel(BaseModel):
    event_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    place_id: Optional[UUID] = None
    points_scored: Optional[int] = None
    points_missed: Optional[int] = None
    number_of_fights: Optional[int] = None

    class Config:
        from_attributes = True


class ResultModel(BaseModel):
    id: UUID
    event_id: UUID
    student: Optional[StudentProfileModel]
    place: Optional[PlaceModel]
    points_scored: int
    points_missed: int
    number_of_fights: int
    average_score: float
    efficiency: float

    class Config:
        from_attributes = True


class EventWithResultModel(BaseModel):
    id: UUID
    name: str
    date_start: datetime.datetime
    date_end: datetime.datetime
    coach_id: UUID
    results: list[ResultModel]

    class Config:
        from_attributes = True
