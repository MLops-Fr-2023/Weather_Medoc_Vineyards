from pydantic import BaseModel

class UserPermission(BaseModel):
    user_id: str
    permission_id: str