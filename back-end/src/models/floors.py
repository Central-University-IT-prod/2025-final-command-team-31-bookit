import json

from typing import Annotated, Any, Optional
from uuid import UUID
from pydantic import BaseModel, model_validator, ValidationError
from fastapi import Form


class FloorBase(BaseModel):
    number: Annotated[int, Form(description="Номер этажа")]
    building_id: Annotated[UUID, Form(description="UUID строения")]

    @model_validator(mode='before')
    @classmethod
    def validate(cls, data: Any) -> Any:
        try:
            if isinstance(data, str):
                data = json.loads(data)
            return data
        except ValidationError:
            raise
        except json.JSONDecodeError:
            raise

class FloorCreate(FloorBase):
    pass

class FloorUpdate(FloorBase):
    number: Annotated[Optional[int], Form(description="Номер этажа")] = None
    building_id: Annotated[Optional[UUID], Form(description="UUID строения")] = None