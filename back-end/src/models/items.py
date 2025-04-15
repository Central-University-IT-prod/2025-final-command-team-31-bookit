from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, model_validator
from uuid import UUID

class CategoryEnum(Enum):
    FOOD = "Еда"
    EQUIPEMENT = "Оборудование"

class PriceTypeEnum(Enum):
    FIXED = "fixed"
    PERHOUR = "perhour"

class GetItems(BaseModel):
    building_id: UUID

class GetItem(BaseModel):
    id: UUID

class PostItem(BaseModel):
    building_id: UUID
    name: str
    price: float
    pricetype: PriceTypeEnum
    category: CategoryEnum

class PatchItem(BaseModel):
    id: UUID
    name: Optional[str] = None
    price: Optional[float] = None
    pricetype: Optional[PriceTypeEnum] = None
    category: Optional[CategoryEnum] = None

class DeleteItem(BaseModel):
    item_id: UUID