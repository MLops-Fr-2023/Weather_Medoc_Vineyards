import uvicorn
from datetime import datetime, timedelta, time, date
from typing import Annotated, Optional, Union, List
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
import pandas as pd
import requests
from snowflake.connector import connect, DictCursor
from methode_sql import *


config = {**dotenv_values(".env_API")}

########## Param Security ##########

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = config['SECRET_KEY']
ALGORITHM = config['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = config['ACCESS_TOKEN_EXPIRE_MINUTES']
WEATHER_API_KEY = config['WEATHER_API_KEY']


############### dB ###############


cities = ['Margaux', 'Soussan', 'Macau, FR', 'Castelnau-de-Medoc','Lamarque, FR', 'Ludon-Medoc', 'Arsac', 'Brach, FR', 'Saint-Laurent Medoc' ]

columns_mandatory = ['observation_time','temperature','weather_code','wind_speed',
                     'wind_degree','wind_dir','pressure','precip','humidity',
                     'cloudcover','feelslike','uv_index','visibility','time','city']

############## Class ##############

class User(BaseModel):
    user_id: str
    pwd_hash: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    user_email: Optional[str] = None
    position: Optional[str] = None
    create_date: Optional[date] = None
    last_upd_date: Optional[date] = None
    active: Optional[bool] = None
    permissions: Optional[List[str]] = []

class UserInDB(User):
    pwd_hash: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Union[str, None] = None

class City(BaseModel):
    name_city: Union[str, None] = None

############## API ##############

app = FastAPI(
    title='Weather API - Château Margaux',
description="API for the weather forecasting around Château Margaux",
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



######### Security Functions ########

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, user_id: str):        
    if user_id in db: 
        user_dict = db[user_id]
        user_dict = {key.lower(): value for key, value in user_dict.items()}
        user_dict['permissions'] = fetch_permissions(user_id)
        return UserInDB(**user_dict)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(users_db, user_id: str, password: str):
    user = get_user(users_db, user_id)
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
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    users_db = fetch_users_from_db()
    #permissions = fetch_permissions(user_id)
    user = get_user(users_db, user_id=token_data.user_id)
    print('user current : ')
    print(user)
    print("")
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

######### Roads Functions #########

async def fetch_data(columns = columns_mandatory, type_request = 'current', API_KEY = WEATHER_API_KEY):
    
    # collect current data and create DataFrame
    df_current = pd.DataFrame(columns = columns)

    # collect current data and create DataFrame
    for city in cities:
        df_tmp = {}
        params = {
            'access_key': API_KEY,
            'query': city 
        }
        api_result = requests.get(f'http://api.weatherstack.com/{type_request}', params)
        response = api_result.json()
        current = response['current']
        df_tmp['observation_time'] = response['location']['localtime']
        df_tmp['temperature'] = current['temperature']
        df_tmp['weather_code'] = current['weather_code']
        df_tmp['wind_speed'] = current['wind_speed']
        df_tmp['wind_degree'] = current['wind_degree']
        df_tmp['wind_dir'] = current['wind_dir']
        df_tmp['pressure'] = current['pressure']
        df_tmp['precip'] = current['precip']
        df_tmp['humidity'] = current['humidity']
        df_tmp['cloudcover'] = current['cloudcover']
        df_tmp['feelslike'] = current['feelslike']
        df_tmp['uv_index'] = current['uv_index']
        df_tmp['visibility'] = current['visibility']
        df_tmp['time'] = current['observation_time']
        df_tmp['city'] = city
        df_tmp = pd.DataFrame(data=df_tmp,index=[0])
        df_current = pd.concat([df_current, df_tmp])

    df_current.reset_index(inplace=True, drop=True)

    # Modify DataFrame to have same strutucre than historical Dataframe
    for i in range(df_current.shape[0]):
        x, y = df_current['observation_time'][i].split(' ')
        df_current['observation_time'][i] = x
        time = datetime.strptime(df_current['time'][i], "%I:%M %p")
        df_current['time'][i] = time.strftime('%H:%M')

    return df_current


############## Roads ##############

@app.get("/")
def read_root():
    """"
    API function: The goal is to allow people living around Margaux Cantenac to acces a 7 days weather features forecast
    """
    return "Welcome to the Joffrey LEMERY, Nicolas CARAYON and Jacques DROUVROY weather API (for places around Margaux-Cantenac)"

@app.post("/token", response_model=Token, tags=['Clients'])
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    users_db = fetch_users_from_db()
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User, tags=['Clients'])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

@app.post("/get_data",  name='Force weather data update', tags=['Backend'])
async def get_data(current_user: Annotated[User, Depends(get_current_active_user)]):

    """Update the current weather data for all cities.
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    # todo : implement permission checking
    if not 'get_data' in current_user.permissions:
        raise Exception(" You don't have the permission"
        )
    print('Identification OK')

    data_list = await fetch_data()
    print(data_list)

    return {'Message' : 'Data successfully updated'}

@app.post("/force_train_model/{city}",  name='Force the train of the model', tags=['Administrators'])
async def force_train_model(city_data: City, current_user: Annotated[User, Depends(get_current_active_user)]):

    """Update the model by training the model - Can take some times (training time).
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    return {'Message' : 'Not released'}

@app.post("/forecast_city/{city}",  name='Forecast 7-days', tags=['Backend'])
async def forecast(city_data: City, current_user: Annotated[User, Depends(get_current_active_user)]):

    """Returns the forecast of weather feature for city = {city}.
    INPUTS :
        city: str 
    OUTPUTS : df with forecast feature overs the next 7-days
    """


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)