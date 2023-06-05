from pydantic import BaseModel
from typing import List

class UserIdPermissionId(BaseModel):
    user_id: str
    permission_id: str