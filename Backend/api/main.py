import os
import uvicorn
import pandas as pd
from fastapi import Body
from typing import Dict, Any
from typing import Annotated
from datetime import timedelta
from business.City import City
from business.Token import Token
from db_access.DbCnx import UserDao
from business.ApiTags import ApiTags
from training.ModelTools import Tools
from business.User import User, UserAdd
from business.KeyReturn import KeyReturn
from security import authent, Permissions
from business.HyperParams import HyperParams
from config.variables import VarEnvSecurApi
from security.Permissions import SpecialUsersID
from business.DataProcessing import UserDataProc
from business.UserPermission import UserPermission
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5000",
    "s3://datalake-weather-castle/mlflow/",
    "https://datalake-weather-castle.s3.eu-west-3.amazonaws.com/mlflow/",
    "https://datalake-weather-castle.s3.eu-west-3.amazonaws.com/mlflow/"
    # Add more allowed origins as needed
]

app = FastAPI(
    title='Weather API - Weather Medoc Vineyards',
    description="API for the weather forecasting around les Châteaux du Médoc",
    version="1.0.1",
    openapi_tags=[
        {
            'name': ApiTags.authentication.value,
            'description': 'Features related to authentication process'
        },
        {
            'name': ApiTags.usersAndPermissions.value,
            'description': 'Features related to users and permissions management'
        },
        {
            'name': ApiTags.weatherData.value,
            'description': 'Features related to Weather data'
        },
        {
            'name': ApiTags.mlModel.value,
            'description': 'Features to manage the ML model lifecycle'
        },
        {
            'name': ApiTags.apiAdmin.value,
            'description': 'Features for the API administrators'
        },
        {
            'name': ApiTags.endUser.value,
            'description': 'Features for the end user'
        }
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables #######################

varenv_securapi = VarEnvSecurApi()


# Routes ###########################

def Handle_Result(result: Dict[str, Any]):
    if KeyReturn.success.value in result:
        if isinstance(result[KeyReturn.success.value], pd.DataFrame):
            result[KeyReturn.success.value] = result[KeyReturn.success.value].to_dict(orient='records')
        return result
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"{result[KeyReturn.error.value]}")


@app.get("/")
def read_root():
    """
    Display API welcome message
    """

    msg = "Welcome to the Joffrey LEMERY, Nicolas CARAYON and Jacques DROUVROY "
    msg += "Forecast Weather API for places around Margaux in Médoc"
    return msg


@app.post("/token", response_model=Token, tags=[ApiTags.authentication.value])
async def get_authent_token(form_data: Annotated[authent.OAuth2PasswordRequestForm, Depends()]):
    """
    Return authentication token
    """
    user = authent.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = {"sub": user.user_id}
    access_token_expires = timedelta(minutes=int(varenv_securapi.access_token_expire_minutes))
    access_token = authent.create_access_token(
        data=data, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User, tags=[ApiTags.authentication.value])
async def get_user_authenticated(current_user: Annotated[User, Depends(authent.get_current_user)]):
    """
    Return authenticated user info
    """
    return current_user


@app.get("/forecast_data/", tags=[ApiTags.endUser.value])
async def get_forecast_data(city: Annotated[City, Depends()],
                            current_user: Annotated[User, Depends(authent.get_current_user)]):
    """
    Return weather forecast data for the city in input for the next 7 days (data from table FORECAST)
    """
    result = UserDao.get_forecast_data_df(city=city.name_city)
    return Handle_Result(result)


@app.get("/get_weather_on_period/", tags=[ApiTags.endUser.value])
async def get_historitical(city: Annotated[City, Depends()], start_date, end_date,
                           current_user: Annotated[User, Depends(authent.get_current_user)]):
    """
    Return historitical weather data for the city in input on the period defined by start_date and end_date
    \nFormat expected for start_date and end_date : 'YYYY-MM-DD'
    """
    result = UserDao.get_hist_data_df(city=city.name_city, start_date=start_date, end_date=end_date)
    print(f"\n result : {result}  \n")

    return Handle_Result(result)


@app.post("/add_user", name='Add user', tags=[ApiTags.usersAndPermissions.value])
async def add_user(user_add: Annotated[UserAdd, Depends()],
                   current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Add user to table USERS
    \nInput : user to add
    """
    if Permissions.Permissions.user_mngt.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    if UserDao.user_exists(user_add.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="USER_ID already exists")

    user_add.pwd_hash = authent.pwd_context.hash(user_add.pwd_hash)

    result = UserDao.add_user(user_add)
    return Handle_Result(result)


@app.post("/add_user_permission", name='Associate permissions to a user', tags=[ApiTags.usersAndPermissions.value])
async def add_user_permission(user_permissions_add: Annotated[UserPermission, Depends()],
                              current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """Add permission to user in table USER_PERMISSION
    \nInputs :
    \n- user_id : user ID
    \n- permission_id : permission ID
    """
    if Permissions.Permissions.user_mngt.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    if user_permissions_add.user_id == Permissions.SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user can't be updated")

    if not UserDao.user_exists(user_permissions_add.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User '{user_permissions_add.user_id}' doesn't exist")

    if user_permissions_add.permission_id not in UserDao.get_permission_ids():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Permission '{user_permissions_add.permission_id}' doesn't exist")

    if UserDao.user_has_permission(user_permissions_add):
        detail_msg = (f"Permission '{user_permissions_add.permission_id}' already given "
                      f"to user '{user_permissions_add.user_id}'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_msg)

    result = UserDao.add_user_permission(user_permissions_add)
    return Handle_Result(result)


@app.post("/edit_user", name='User edition', tags=[ApiTags.usersAndPermissions.value])
async def edit_user(user: Annotated[UserAdd, Depends()],
                    current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Edit user in table USERS
    Inputs :
    \n user : user to edit
    """

    if Permissions.Permissions.user_mngt.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    if user.user_id == Permissions.SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user can't be updated")

    if not UserDao.user_exists(user.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User '{user.user_id}' doesn't exist")

    user.pwd_hash = authent.pwd_context.hash(user.pwd_hash)
    result = UserDao.edit_user(user)
    return Handle_Result(result)


@app.post("/delete_user", name='Delete a user from the dB', tags=[ApiTags.usersAndPermissions.value])
async def delete_user(user_id: str, current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Delete user from table USERS
    Inputs :
    \nuser to add : Dictionnary
    """

    if Permissions.Permissions.user_mngt.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    if user_id == Permissions.SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user can't be deleted")

    if not UserDao.user_exists(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User doesn't exist")

    result = UserDao.delete_user(user_id)
    return Handle_Result(result)


@app.post("/delete_user_permission", name='Remove permission to user', tags=[ApiTags.usersAndPermissions.value])
async def delete_user_permission(user_permissions: Annotated[UserPermission, Depends()],
                                 current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Delete permission_id for user_id from table USER_PERMISSION
    """

    if Permissions.Permissions.user_mngt.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    if user_permissions.user_id == Permissions.SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user_permission can't be deleted")

    if not UserDao.user_has_permission(user_permissions):
        detail_msg = (f"User '{user_permissions.user_id}' "
                      f"has no permission '{user_permissions.permission_id}'")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_msg)

    result = UserDao.delete_user_permission(user_permissions)
    return Handle_Result(result)


@app.post("/get_logs", name='Get logs', tags=[ApiTags.apiAdmin.value])
async def get_logs(current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Get API logs
    """

    if current_user.user_id != SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    return UserDao.get_logs()


@app.get("/db_env", name='Get database environment info', tags=[ApiTags.apiAdmin.value])
def get_db_info(current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Return info about SQL Database to determine the running environment
    """

    if current_user.user_id != SpecialUsersID.administrator.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    return {
        "DB_MYSQL_HOST": os.getenv('DB_MYSQL_HOST'),
        "MYSQL_DATABASE": os.getenv('MYSQL_DATABASE'),
        "DB_MYSQL_USER": os.getenv('DB_MYSQL_USER'),
    }


@app.post("/populate_weather_table", name='Populate table WEATHER_DATA with historical data from Weather API',
          tags=[ApiTags.weatherData.value])
async def populate_weather_table(current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Populate table WEATHER_DATA with historical data from weatherstack.com
    \nInputs :
    \ncurrent user : authenticated user
    """

    if Permissions.Permissions.get_data.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    result = await UserDataProc.insert_weather_data_historical()

    return Handle_Result(result)


@app.post("/update_weather_data", name='Update database with data from Weather API', tags=[ApiTags.weatherData.value])
async def upd_weather_data(current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Update table WEATHER_DATA with current data from weatherstack API for all cities
    \nInputs :
    \ncurrent user : authenticated user
    """

    if Permissions.Permissions.get_data.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    result = await UserDataProc.update_weather_data()
    return Handle_Result(result)


@app.post("/delete_weather_data", name='Empty table WEATHER_DATA', tags=[ApiTags.weatherData.value])
async def delete_weather_data(current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Empty table WEATHER_DATA
    """

    if Permissions.Permissions.get_data.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    result = await UserDao.empty_weather_data()
    return Handle_Result(result)


@app.post("/delete_forecast_data", name='Empty table FORECAST', tags=[ApiTags.weatherData.value])
async def delete_forecast_data(current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Empty table FORECAST_DATA
    """

    if Permissions.Permissions.get_data.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")
    result = await UserDao.empty_forecast_data()
    return Handle_Result(result)


@app.post("/forecast_city/{city}", name='Set weather forecast of the next 7 days for city into FORECAST table',
          tags=[ApiTags.weatherData.value])
async def forecast(city: Annotated[City, Depends()],
                   current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Return the forecast of weather for city in input
    \nInputs : city
    """

    if Permissions.Permissions.forecast.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    result = await Tools.get_forecast(city=city.name_city)

    return Handle_Result(result)


@app.post("/train_model/{city}", name='Launch model training with a given set of hyperparameters',
          tags=[ApiTags.mlModel.value])
async def train_model(city: Annotated[City, Depends()], hyper_params: HyperParams,
                      train_label: str, current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Launch model training with the hyperparameters given in parameters
    """

    if Permissions.Permissions.training.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    result = Tools.train_model(city=city.name_city, hyper_params=hyper_params, train_label=train_label)
    return Handle_Result(result)


@app.post("/train_models/{city}", name='Launch several trainings for hyperparameters optimization',
          tags=[ApiTags.mlModel.value])
async def train_models(city: Annotated[City, Depends()], train_label: str,
                       current_user: Annotated[User, Depends(authent.get_current_active_user)],
                       hyper_params_dict: Dict[str, HyperParams] = Body(...)):

    """
    Launch trainings of the model with the sets of hyperparameters defined in hyper_params_dict (one training per set)
    """

    if Permissions.Permissions.training.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    result = Tools.launch_trainings(city=city.name_city, hyper_params_dict=hyper_params_dict, train_label=train_label)
    return Handle_Result(result)


@app.post("/retrain_model/{city}", name='Launch a retraining of the model', tags=[ApiTags.mlModel.value])
async def retrain_model(city: Annotated[City, Depends()], n_epochs: int,
                        current_user: Annotated[User, Depends(authent.get_current_active_user)]):

    """
    Launch a new train of current model on new data
    """

    if Permissions.Permissions.training.value not in current_user.permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have the permission")

    result = Tools.retrain(city=city.name_city, n_epochs=n_epochs)
    return Handle_Result(result)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
