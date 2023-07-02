from pydantic import BaseModel
from typing import Union

class City(BaseModel):
    name_city: Union[str, None] = "Margaux"