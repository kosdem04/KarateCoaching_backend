from pydantic import BaseModel
from typing import Optional
import datetime
from src.schemas.base import TypeEventModel
from uuid import UUID



class AddEventModel(BaseModel):
    name: str
    type_id: UUID
    date_start: datetime.date
    date_end: datetime.date

    class Config:
        from_attributes = True



class EditEventModel(BaseModel):
    name: Optional[str] = None
    type_id: Optional[UUID] = None
    date_start: Optional[datetime.datetime] = None
    date_end: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class EventSimpleModel(BaseModel):
    id: UUID
    name: str
    type_id: UUID
    date_start: datetime.datetime
    date_end: datetime.datetime
    coach_id: UUID

    class Config:
        from_attributes = True


class EventModel(BaseModel):
    id: UUID
    name: str
    type: Optional[TypeEventModel]
    date_start: datetime.datetime
    date_end: datetime.datetime
    coach_id: UUID

    class Config:
        from_attributes = True
