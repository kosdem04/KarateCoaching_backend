from pydantic import BaseModel, EmailStr
import datetime
from typing import Optional
from uuid import UUID


class UserRegisterModel(BaseModel):
    first_name: str
    patronymic: Optional[str]
    last_name: str
    email: EmailStr
    date_of_birth: datetime.date


class UserLoginModel(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ResulSimpleModel(BaseModel):
    event_id: UUID
    student_id: UUID
    place_id: UUID
    points_scored: int
    points_missed: int
    number_of_fights: int
    average_score: float
    efficiency: float

    class Config:
        from_attributes = True


class StudentModel(BaseModel):
    id: UUID
    first_name: str
    patronymic: Optional[str]
    last_name: str
    email: EmailStr
    date_of_birth: Optional[datetime.date]
    phone_number: Optional[str]
    img_url: str

    class Config:
        from_attributes = True


class PlaceModel(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True


class TypeEventModel(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True