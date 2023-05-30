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



########## Param Security ##########


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        "disabled": False,
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

class Data(BaseModel):
    XXXXX: Union[str, None] = None
    XXXXX: Union[str, None] = None
    XXXXX: Union[str, None] = None
    XXXXX: Union[str, None] = None
    XXXXX: Union[str, None] = None
    XXXXX: Union[str, None] = None
    XXXXX: Union[str, None] = None 
    XXXXX: Union[str, None] = None 


############## API ##############

app = FastAPI(
    title='QCM API',
    description="My own API for the FAST API exam",
    version="1.0.1",
    openapi_tags=[
    {
        'name': 'Clients',
        'description': 'Fonction related to getting QCMs'
    },
    {
        'name': 'Administrators',
        'description': 'functions related to admins'
    }])
