import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from datetime import timedelta
from db_access.DbCnx import UserDao
from security import authent, Permissions
from typing import Annotated
from config import conf
from business.User import User, UserAdd
from business.UserPermission import UserPermission
from business.Token import Token
from business.City import City
from business.DataProcessing import UserDataProc
from business.HyperParams import HyperParams
from training.ModelTools import Tools
from security.Permissions import SpecialUsersID
from typing import Dict
from fastapi import Body

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
async def add_user(user_add : Annotated[UserAdd, Depends()], current_user: Annotated[User, Depends(authent.get_current_active_user)]):
 
    """Add user to table USERS
    INPUTS :
         user to add : Dictionnary
    OUTPUTS : User added in Snowflake - Users dB
    """
    if not Permissions.Permissions.user_mngt.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    if UserDao.user_exists(user_add.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="USER_ID already exists")
    
    user_add.pwd_hash = authent.pwd_context.hash(user_add.pwd_hash)
    
    return UserDao.add_user(user_add)
      
@app.post("/add_user_permission",  name='Associate permissions to a user', tags=['Administrators'])
async def add_user_permission(user_permissions_add : Annotated[UserPermission, Depends()], current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Give permission to user in table USER_PERMISSION
    INPUTS :
         user_id : user ID
         permission_id : permission ID
    OUTPUTS : User_permissions added in Snowflake -  User_permission dB
    """
    if not Permissions.Permissions.user_mngt.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    if user_permissions_add.user_id == Permissions.SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user can't be updated")

    if not UserDao.user_exists(user_permissions_add.user_id) :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User '{user_permissions_add.user_id}' doesn't exist")

    if user_permissions_add.permission_id not in UserDao.get_permission_ids():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"Permission '{user_permissions_add.permission_id}' doesn't exist")

    if UserDao.user_has_permission(user_permissions_add) :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"Permission '{user_permissions_add.permission_id}' already given to user '{user_permissions_add.user_id}'")

    return UserDao.add_user_permission(user_permissions_add)           
    
@app.post("/edit_user",  name='User edition', tags=['Administrators'])
async def edit_user(user : Annotated[UserAdd, Depends()], current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Edit a user in table USERS
    INPUTS :
         user to modify : Dictionnary
    OUTPUTS : User modified in Snowflake - Users dB
    """

    if not Permissions.Permissions.user_mngt.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    if user.user_id == Permissions.SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user can't be updated")
    
    if not UserDao.user_exists(user.user_id) :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User '{user.user_id}' doesn't exist")

    user.pwd_hash = authent.pwd_context.hash(user.pwd_hash)
    return UserDao.edit_user(user)

@app.post("/delete_user",  name='Delete a user from the dB', tags=['Administrators'])
async def delete_user(user_id : str, current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Delete user from table USERS
    INPUTS :
         user to add : Dictionnary
    OUTPUTS : User added in Snowflake - Users dB 
    """

    if not Permissions.Permissions.user_mngt.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    if user_id == Permissions.SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user can't be deleted")
    
    if not UserDao.user_exists(user_id) :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exist")

    return UserDao.delete_user(user_id)
    
@app.post("/delete_user_permission",  name='Remove permission to user', tags=['Administrators'])
async def delete_user_permission(user_permissions : Annotated[UserPermission, Depends()], current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Delete a user from table USERS and his permissions from table USER_PERMISSION
    INPUTS :
         user to add : Dictionnary
    OUTPUTS : User added in Snowflake - Users dB 
    """
    if not Permissions.Permissions.user_mngt.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    if user_permissions.user_id == Permissions.SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user_permission can't be deleted")
    
    if not UserDao.user_has_permission(user_permissions) :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User '{user_permissions.user_id}' has no permission '{user_permissions.permission_id}'")
    
    return UserDao.delete_user_permission(user_permissions)
    
@app.post("/get_logs",  name='Get logs', tags=['Administrators'])
async def get_logs(current_user: Annotated[User, Depends(authent.get_current_active_user)]):
    """Get log file"""
    
    if current_user.user_id != SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    return UserDao.get_logs()

@app.post("/populate_weather_table",  name='Populate wheather table with historical data from Weather API', tags=['Backend'])
async def populate_weather_table(current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Update table WEATHER_DATA with current data from Wheather API for all cities
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    
    if not Permissions.Permissions.get_data.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    return await UserDataProc.insert_weather_data_historical()

@app.post("/update_weather_data",  name='Update database with data from Weather API', tags=['Backend'])
async def upd_weather_data(current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Update table WEATHER_DATA with current data from Wheather API for all cities
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    
    if not Permissions.Permissions.get_data.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    return await UserDataProc.update_weather_data()

@app.post("/delete_weather_data",  name='Delete all weather data from database', tags=['Backend'])
async def delete_weather_data(current_user: Annotated[User, Depends(authent.get_current_active_user)]):
    """Empty table WEATHER_DATA """
    
    if not Permissions.Permissions.get_data.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    return UserDao.empty_weather_data()

@app.post("/forecast_city/{city}",  name='Forecast 7-days', tags=['Backend'])
async def forecast(city: Annotated[City, Depends()], current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Returns the forecast of weather feature for city = {city}.
    INPUTS :
        city: str 
    OUTPUTS : df with forecast feature overs the next 7-days
    """

    if not Permissions.Permissions.forecast.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    try:
        df = Tools.get_forecast(city = city.name_city)
        return df
    except Exception as e:
        return {'error': 'Forecast failed'}    

@app.post("/train_model/{city}",  name='Launch model training with a given set of hyperparamaters', tags=['Backend'])
async def train_model(city: Annotated[City, Depends()], hyper_params: HyperParams, train_label:str, current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Update the model by training it - Can take some times (training time)
    INPUTS :
        current user : str 
    OUTPUTS : Data updated in Snowflake
    """
    if not Permissions.Permissions.training.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    return Tools.train_model(city=city.name_city, hyper_params=hyper_params, train_label='iteration_label')    

@app.post("/train_models/{city}",  name='Launch several trainings for hyperparameters optimization', tags=['Backend'])
async def train_models(city: Annotated[City, Depends()], current_user: Annotated[User, Depends(authent.get_current_active_user)], hyper_params_dict: Dict[str, HyperParams] = Body(...)):
    """Launch trainings of the model with the hyperparameters defined in hyper_params_dict"""

    if not Permissions.Permissions.training.value in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    
    try:
        return Tools.launch_trainings(city=city.name_city, hyper_params_dict=hyper_params_dict)               
    except Exception as e:
        return {'error': 'launch_trainings failed'}    


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)