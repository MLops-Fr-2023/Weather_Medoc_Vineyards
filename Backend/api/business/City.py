from pydantic import BaseModel
from typing import Annotated, Optional, Union, List

class City(BaseModel):
    name_city: Union[str, None] = None