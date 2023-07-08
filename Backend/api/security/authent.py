
from typing import Union
from typing import Annotated
from jose import jwt, JWTError
from dotenv import dotenv_values
from db_access.DbCnx import UserDao
from business.Token import TokenData
from passlib.context import CryptContext
from datetime import timedelta, datetime
from business.User import User, UserInDB
from fastapi import Depends, HTTPException, status
from config.variables import varenv_securapi, varenv_weather_api
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

#Import des variables
varenv_securapi = varenv_securapi()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(user_id: str, password: str):
    user = UserDao.get_user(user_id)
    if not user:
        return False
    if not verify_password(password, user.pwd_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, varenv_securapi.secret_key, algorithm=varenv_securapi.algorithm)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, varenv_securapi.secret_key, algorithms=varenv_securapi.algorithm)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    user = UserDao.get_user(token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user