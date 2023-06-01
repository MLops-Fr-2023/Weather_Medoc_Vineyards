import uvicorn
from datetime import datetime, timedelta,time
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
import pandas as pd
import requests
from snowflake.connector import connect


config = {**dotenv_values(".env_API")} # config = {"USER": "foo", "EMAIL": "foo@example.org"}
print(config)

########## Param Security ##########

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = config['SECRET_KEY']
ALGORITHM = config['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = config['ACCESS_TOKEN_EXPIRE_MINUTES']
WEATHER_API_KEY = config['WEATHER_API_KEY']

########### Snowflake #############

snowflake_config = {
    "user": "<your_username>",
    "password": "<your_password>",
    "account": "<your_account>",
    "warehouse": "<your_warehouse>",
    "database": "<your_database>",
    "schema": "<your_schema>"
}

############### dB ###############


users_db = {

    "Aiflow_train": {
        "username": "airflow_train",
        "hashed_password": pwd_context.hash('XXXXX'),
        "position": 'client',
        "forecast": False,
        "get_data": False,
        "training": True,
        "disabled": False
    },

    "Aiflow_get_data" : {
        "username" :  "airflow_get_data",
        "hashed_password" : pwd_context.hash('XXXXX'),
        "position": 'client',
        "forecast": False,
        "get_data": True,
        "training": False,
        "disabled": False
    },

    "admax" : {
        "username" :  "admax",
        "hashed_password" : pwd_context.hash('XXXXX'),
        "position": 'Admin',
        "forecast": True,
        "get_data": True,
        "training": True,
        "disabled": False
    },

    "user" : {
        "username" :  "user",
        "hashed_password" : pwd_context.hash('XXXXX'),
        "position": 'Admin',
        "forecast": True,
        "get_data": False,
        "training": False,
        "disabled": False
    }

}

cities = ['Margaux', 'Soussan', 'Macau, FR', 'Castelnau-de-Medoc','Lamarque, FR', 'Ludon-Medoc', 'Arsac', 'Brach, FR', 'Saint-Laurent Medoc' ]

columns_mandatory = ['observation_time','temperature','weather_code','wind_speed',
                     'wind_degree','wind_dir','pressure','precip','humidity',
                     'cloudcover','feelslike','uv_index','visibility','time','city']

############## Class ##############

class User(BaseModel):
    username: str
    position: Union[str, None] = None
    forecast: Union[bool, None] = None
    get_data: Union[bool, None] = None
    training: Union[bool, None] = None
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


######### Security Functions ########


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



@app.post("/get_data",  name='Force weather data update', tags=['Backend'])
async def get_data(current_user: Annotated[User, Depends(get_current_active_user)]):

    """Update the current weather data for all cities.
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    if current_user.get_data == True:
        print('Identification ok')
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