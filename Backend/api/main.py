import uvicorn
from fastapi import FastAPI, Form, File, Response, Header, UploadFile, Depends, HTTPException, status, Query
from jose import JWTError, jwt
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import datetime, timedelta, time, date
import random
import json
import os
import pandas as pd
import requests
from snowflake.connector import connect, DictCursor
from db_access.DbCnx import UserDao
from security import authent, Permissions
# from security.Permissions import PermissionsRefs
from typing import Annotated, Optional, Union, List
from config import conf
from business import References
from business.User import User
from business.UserPermission import UserPermission
from business.UserIdPermId import UserIdPermissionId
from business.Token import Token
from business.City import City


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


async def fetch_data(columns = References.columns_mandatory, type_request = 'current', API_KEY = conf.WEATHER_API_KEY):
    
    # collect current data and create DataFrame
    df_current = pd.DataFrame(columns = columns)

    # collect current data and create DataFrame
    for city in References.cities:
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
async def login(form_data: Annotated[authent.OAuth2PasswordRequestForm, Depends()]):
    
    user = authent.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(conf.ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = authent.create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User, tags=['Clients'])
async def read_users_me(current_user: Annotated[User, Depends(authent.get_current_user)]):
    return current_user

@app.post("/add_user",  name='Add user', tags=['Administrators'])
async def add_user(user_add : Annotated[User, Depends()], current_user: Annotated[User, Depends(authent.get_current_active_user)]):
 
    """Add user to table USERS
    INPUTS :
         user to add : Dictionnary
    OUTPUTS : User added in Snowflake - Users dB and User_permission dB
    """
    if not Permissions.Permissions.user_mngt.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
        
    user_add.pwd_hash = authent.pwd_context.hash(user_add.pwd_hash)
    UserDao.add_user(user_add)

    return {'Message' : f"User {user_add.user_id} successfully added"}

@app.post("/add_user_permission",  name='Associate permissions to a user', tags=['Administrators'])
async def add_user_permission(user_permissions_add : Annotated[UserIdPermissionId, Depends()], current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Associates some permissions to a existing user.
    INPUTS :
         user_id
         permission_id
    OUTPUTS : User_permissions added in Snowflake -  User_permission dB
    """
    if not Permissions.Permissions.user_mngt.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    UserDao.add_user_permission(user_permissions_add.user_id, user_permissions_add.permission_id)

    return {'Message' : 'User_permissions successfully added'}

@app.post("/edit_user",  name='User edition', tags=['Administrators'])
async def edit_user(user : Annotated[User, Depends()], current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Edit a user in table USERS
    INPUTS :
         user to modify : Dictionnary
    OUTPUTS : User modified in Snowflake - Users dB and User_permission dB
    """

    if not Permissions.Permissions.user_mngt.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    try:
        UserDao.edit_user(user)
        print(f"User {user.user_id} correctly updated")
        return {'Message' : 'User successfully modified'}
    except:
        print(f"Failed tp update user {user.user_id}")
        return {'Message' : f"Failed to update {user.user_id}"}
    finally:
        return

@app.post("/delete_user",  name='Delete a user from the dB', tags=['Administrators'])
async def delete_user(user_id : str, current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Delete user from table USERS
    INPUTS :
         user to add : Dictionnary
    OUTPUTS : User added in Snowflake - Users dB 
    """

    if not Permissions.Permissions.user_mngt.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    if user_id == 'admax':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user can't be deleted")
    try:
        UserDao.delete_user(user_id)
        UserDao.delete_user_permissions(user_id)
    except:
        return {'Message' : f"User {user_id} deletion failed"}
    finally:
        return {'Message' : f"User {user_id} and related permissions successfully deleted"}

@app.post("/get_data",  name='Update database with data from Wheather API', tags=['Backend'])
async def get_data(current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Update the current weather data for all cities.
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    if not Permissions.Permissions.get_data in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    data_list = await fetch_data()

    return {'Message' : 'Data successfully updated'}

@app.post("/train_model/{city}",  name='Force the train of the model', tags=['Administrators'])
async def train_model(city_data: City, current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Update the model by training it - Can take some times (training time).
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    return {'Message' : 'Not released'}

@app.post("/forecast_city/{city}",  name='Forecast 7-days', tags=['Backend'])
async def forecast(city_data: City, current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Returns the forecast of weather feature for city = {city}.
    INPUTS :
        city: str 
    OUTPUTS : df with forecast feature overs the next 7-days
    """


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)