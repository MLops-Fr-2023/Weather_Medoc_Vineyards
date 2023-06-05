from pydantic import BaseModel
from typing import Annotated, Optional, Union, List

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Union[str, None] = None