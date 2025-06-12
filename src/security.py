from passlib.context import CryptContext
import datetime
from authlib.jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from src.config import SECURITY_ALGORITHM, SECURITY_SECRET_KEY
import string
import secrets
import random


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def generate_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_reset_code(length: int = 6) -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


def create_access_token(data: dict, expires_delta: datetime.timedelta = datetime.timedelta(hours=5)):
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "exp": now + expires_delta,
        "iat": now,
        "sub": data["sub"],
    }
    return jwt.encode({"alg": SECURITY_ALGORITHM}, payload, SECURITY_SECRET_KEY).decode("utf-8")


security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        claims = jwt.decode(token, SECURITY_SECRET_KEY)
        claims.validate()  # проверяет срок жизни
        return claims["sub"]
    except Exception as e:
        print('Ошибка ', e)
        raise HTTPException( status_code=401, detail="Недействительный токен")



# async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     try:
#         claims = jwt.decode(token, SECRET_KEY)
#         claims.validate()
#         if claims.get("role") != "admin":
#             raise HTTPException(status_code=403, detail="Нет доступа")
#         return claims["sub"]
#     except Exception:
#         raise HTTPException(status_code=401, detail="Недействительный токен")