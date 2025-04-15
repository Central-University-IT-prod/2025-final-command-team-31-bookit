from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, model_validator
from uuid import UUID


class GetSuggestion(BaseModel):
    building_id: UUID

class PutSuggestions(BaseModel):
    building_id: UUID
    txt: List[str]