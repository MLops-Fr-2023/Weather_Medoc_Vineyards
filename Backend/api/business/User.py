from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class User(BaseModel):
    user_id: str
    pwd_hash: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    user_email: Optional[str] = None
    position: Optional[str] = None
    create_date: Optional[date] =  datetime.now().strftime("%Y-%m-%d")
    last_upd_date: Optional[date] = datetime.now().strftime("%Y-%m-%d")
    active: Optional[bool] = True
    permissions: Optional[list[str]] = []

class UserInDB(User, BaseModel):
    pwd_hash: str

    
class UserAdd(BaseModel):
    user_id: str
    pwd_hash: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    user_email: Optional[str] = None
    position: Optional[str] = None
    active: Optional[bool] = True
