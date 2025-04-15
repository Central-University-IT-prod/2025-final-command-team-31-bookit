from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, model_validator
from uuid import UUID


class GetSeats(BaseModel):
    floor_id: UUID

class PutSeatsItem(BaseModel):
    id: Optional[UUID]=None
    posx: float
    posy: float
    name: str
    onlyempl: bool
    price_g: float
    price_e: float

class PutSeats(BaseModel):
    floor_id: UUID
    seats: List[PutSeatsItem]