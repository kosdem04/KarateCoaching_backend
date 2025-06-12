from pydantic import BaseModel, EmailStr
import datetime
from typing import Optional


class GenerateResetPasswordCodeModel(BaseModel):
    email: EmailStr



class ResetPasswordModel(BaseModel):
    code: str
    new_password: str
    repeat_new_password: str
