from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.security import get_current_user



SessionDep = Annotated[AsyncSession, Depends(get_session)]
AuthUserDep = Annotated[str, Depends(get_current_user)]

