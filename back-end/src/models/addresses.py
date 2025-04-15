from typing import Annotated
from pydantic import BaseModel, Field

# Модели данных
class AddressCreate(BaseModel):
    name: Annotated[str, Field(description="Название адреса")]
    lon: Annotated[float, Field(description="Долгота")]
    lat: Annotated[float, Field(description="Широта")]