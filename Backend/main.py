import uvicorn
from datetime import datetime, timedelta
from typing import Annotated, Optional, Union
from fastapi.security import OAuth2PasswordBearer, HTTPBasic, HTTPBasicCredentials, OAuth2PasswordRequestForm
from fastapi import FastAPI, Form, File, Response, Header, UploadFile, Depends, HTTPException, status, Query
from passlib.context import CryptContext
from jose import JWTError, jwt
import numpy as np
import pandas as pd
from pydantic import BaseModel
import random
import json
import os
from dotenv import dotenv_values


config = {**dotenv_values(".env_API")} # config = {"USER": "foo", "EMAIL": "foo@example.org"}
print(config)
########## Param Security ##########


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = config['SECRET_KEY']
ALGORITHM = config['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = config['ACCESS_TOKEN_EXPIRE_MINUTES']

############## dB ##############


users_db = {

    "Aiflow_train": {
        "username": "airflow_train",
        "hashed_password": pwd_context.hash('XXXXX'),
        "position": 'client',
        "disabled": False,
    },

    "Aiflow_train" : {
        "username" :  "airflow_get_data",
        "hashed_password" : pwd_context.hash('XXXXX'),
        "position": 'client',
        "disabled": False,
    },

    "admax" : {
        "username" :  "admax",
        "hashed_password" : pwd_context.hash('XXXXX'),
        "position": 'Admin',
        "disabled": True,
    }
}

############## Class ##############

class User(BaseModel):
    username: str
    position: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class City(BaseModel):
    name_city: Union[str, None] = None

# class Data(BaseModel):
#     XXXXX: Union[str, None] = None
#     XXXXX: Union[str, None] = None
#     XXXXX: Union[str, None] = None
#     XXXXX: Union[str, None] = None
#     XXXXX: Union[str, None] = None
#     XXXXX: Union[str, None] = None
#     XXXXX: Union[str, None] = None 
#     XXXXX: Union[str, None] = None 


############## API ##############

app = FastAPI(
    title='Weather API - Margaux Castle',
description="API for the weather forecasting around Margaux Castle",
    version="1.0.1",
    openapi_tags=[
    {
        'name': 'Backend',
        'description': 'Functions related to backend functionnalities'
    },

        {
        'name': 'Frontend',
        'description': 'Functions related to frontend functionnalities'
    },

        {
        'name': 'Clients',
        'description': 'Functions related to clients'
    },

    {
        'name': 'Administrators',
        'description': 'Functions related to admins'
    }])



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(users_db, username: str, password: str):
    user = get_user(users_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config['SECRET_KEY'], algorithm=config['ALGORITHM'])
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config['SECRET_KEY'], algorithms=config['ALGORITHM'])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user



async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user





############## Roads ##############

@app.get("/")
def read_root():
    """"
    API function: The goal is to allow people living around Margaux Cantenac to acces a 7 days weather features forecast
    """
    return "Welcome to the Joffrey LEMERY, Nicolas CARAYONS and Jacques Douvroy weather API (for places around Margaux-Cantenac)"



@app.post("/token", response_model=Token, tags=['Clients'])
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/users/me/", response_model=User, tags=['Clients'])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user



@app.post("/force_data_update",  name='Force weather data update', tags=['Administrators'])
async def force_data_update(current_user: Annotated[User, Depends(get_current_active_user)]):

    """Update the current weather data for all cities.
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    return {'Message' : 'Not released'}

@app.post("/force_train_model/{city}",  name='Force the train of the model', tags=['Administrators'])
async def force_data_update(city_data: City, current_user: Annotated[User, Depends(get_current_active_user)]):

    """Update the model by training the model - Can take some times (training time).
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    return {'Message' : 'Not released'}

@app.post("/forecast_city/{city}",  name='Forecast 7-days', tags=['Backend'])
async def forecast(city_data: City):

    """Returns the forecast of weather feature for city = {city}.
    INPUTS :
        city: str 
    OUTPUTS : df with forecast feature overs the next 7-days
    """



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)