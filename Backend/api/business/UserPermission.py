from pydantic import BaseModel
from typing import List

class UserPermission(BaseModel):
    user_id: str
    permissions_id: list[str] = None