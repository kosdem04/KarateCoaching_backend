from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class GroupModel(BaseModel):
    id: UUID
    name: str
    coach_id: UUID
    class Config:
        from_attributes = True


class AddGroupModel(BaseModel):
    name: str

    class Config:
        from_attributes = True


class EditGroupModel(BaseModel):
    name: Optional[str] = None


class AddStudentInGroupModel(BaseModel):
    group_id: UUID
    student_id: UUID

    class Config:
        from_attributes = True

